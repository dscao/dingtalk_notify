import logging
import time
import requests
import json
import os
import base64
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_DATA,
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_RESOURCE

_LOGGER = logging.getLogger(__name__)
DIVIDER = "———————————"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({    
    vol.Required("appkey"): cv.string,
    vol.Required("appsecret"): cv.string,
    vol.Required("touser"): cv.string,
    vol.Optional(CONF_RESOURCE, default = "https://api.dingtalk.com"): cv.url,
    vol.Optional("resource_username", default = ""): cv.string,
    vol.Optional("resource_password", default = ""): cv.string,
    vol.Optional("https_proxies", default = ""): cv.string,

})


def get_service(hass, config, discovery_info=None):
    return DingtalkNotificationService(
        hass,
        config.get("appkey"),        
        config.get("appsecret"),
        config.get("touser"),
        config.get(CONF_RESOURCE),
        config.get("resource_username"),
        config.get("resource_password"),
        config.get("https_proxies"),
    )


class DingtalkNotificationService(BaseNotificationService):
    def __init__(self, hass, appkey, appsecret, touser, dingtalkbaseurl, resource_username, resource_password, https_proxies):
        self._appkey = appkey
        self._appsecret = appsecret
        self._touser = touser
        self._dingtalkbaseurl = dingtalkbaseurl
        self._httpsproxies = { "https": https_proxies } 
        self._token = ""
        self._token_expire_time = 0

        if resource_username and resource_password:
            self._header = {"Authorization": "Basic {}".format(self.getAuth(resource_username,resource_password)),"Content-Type": "application/json"} 
        else:
            self._header = {"Content-Type": "application/json"}
        
        
    def getAuth(self,uername,password):
        serect = uername + ":"+password
        bs = str(base64.b64encode(serect.encode("utf-8")), "utf-8")
        return bs

    def _get_access_token(self):
        _LOGGER.debug("Getting token.")
        url = self._dingtalkbaseurl + "/v1.0/oauth2/accessToken"
        values = {
            "appKey": self._appkey,
            "appSecret": self._appsecret,
        }
        send_values = bytes(json.dumps(values), "utf-8")
        req = requests.post(url, send_values, headers=self._header, proxies=self._httpsproxies)        
        if req.status_code not in (200, 201):
            _LOGGER.exception(
                "获取钉钉 Access token 失败. Response %s:", req)
        data = json.loads(req.text)
        self._token_expire_time = time.time() + data["expireIn"]
        _LOGGER.debug("获取钉钉 Access token :" + str(data) )
        return data["accessToken"]

    def get_access_token(self):
        if time.time() < self._token_expire_time:
            return self._token
        else:
            self._token = self._get_access_token()
            return self._token

    def send_message(self, message="", **kwargs):
        send_url = self._dingtalkbaseurl + "/v1.0/robot/oToMessages/batchSend"
        
        self._header["x-acs-dingtalk-access-token"] = self.get_access_token()
        
        title = kwargs.get(ATTR_TITLE)

        data = kwargs.get(ATTR_DATA) or {}
        msgtype = data.get("type", "sampleText")
        url = data.get("url")
        picurl = data.get("picurl")
        videopath = data.get("videopath")
        imagepath = data.get("imagepath")
        safe = data.get("safe") or 0
        touser = kwargs.get(ATTR_TARGET) or self._touser
        if not isinstance(touser, list):
            touser = touser.split("|")


        if msgtype == "sampleText":
            content = ""
            if title is not None:
                content += f"{title}\n{DIVIDER}\n"
            content += message
            msg = str({"content": content})
        elif msgtype == "sampleMarkdown":
            msg = str({"title": title, "text": message})
        elif msgtype == "sampleImageMsg":
            msg = str({"photoURL": picurl})
        elif msgtype == "sampleLink":
            if self._dingtalkbaseurl: 
                uploadurl = self._dingtalkbaseurl
            else:
                uploadurl = "https://oapi.dingtalk.com"
                
            curl = (
                uploadurl + "/media/upload?access_token="
                + self.get_access_token()
                + "&type=image"
            )
            if imagepath and os.path.isfile(imagepath):
                files = {"media": open(imagepath, "rb")}
                data = {'type': 'file'}
                try:
                    r = requests.post(curl, files=files, data=data, proxies=self._httpsproxies, timeout=(20,180))
                    _LOGGER.debug("Uploading media " + imagepath + " to Dingtalk servicers:"+ r.text)
                except requests.Timeout: 
                    _LOGGER.error("File upload timeout, please try again later.")
                    return                
                media_id = json.loads(r.text)["media_id"]

            msg = str({"text": message, "title": title, "picUrl": media_id, "messageUrl": url})
        elif msgtype == "sampleActionCard":
            msg = str({"title": title, "text": message, "singleTitle": "查看详情", "singleURL": url})

        else:
            raise TypeError("消息类型输入错误，请输入：sampleText/sampleMarkdown/sampleImageMsg/sampleLink/sampleActionCard")

        send_values = {
          "robotCode" : self._appkey,
          "userIds" : touser,
          "msgKey" : msgtype,
          "msgParam" : msg
        }
        _LOGGER.debug(send_values)
        send_msges = bytes(json.dumps(send_values), "utf-8")
        response = requests.post(send_url, send_msges, headers=self._header, proxies=self._httpsproxies)
        if response.status_code not in (200, 201):
            _LOGGER.exception(
                "Error sending message. Response %d: %s:",
                response.status_code, response.reason)
        res = response.json()
        _LOGGER.debug(str(res))
        # if response["errcode"] != 0:
            # _LOGGER.error(response)
        # else:
            # _LOGGER.debug(response)
