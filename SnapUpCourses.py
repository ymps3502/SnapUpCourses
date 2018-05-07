#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
# import json
from pprint import pprint
from collections import defaultdict


class SnapUpCourses(object):
    """docstring for SnapUpCourses"""

    def __init__(self, user):
        super(SnapUpCourses, self).__init__()
        self.userId = user.id
        self.userPassword = user.password
        self.req = requests.Session()
        self.rep = ''
        self.baseLink = 'https://onepiece2.nchu.edu.tw/cofsys/plsql/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/55.0.2883.87 Safari/537.36'
        }
        if self.login(self.userId, self.userPassword):
            print("login successfully")
        else:
            print("login fail")
        # resp = requests.get(
        #   "https://onepiece.nchu.edu.tw/cofsys/plsql/json_for_course?p_career=O"
        # )
        # self.courseJsonData = json.loads(resp.text)
        # pprint(self.courseJsonData)

    def login(self, userId, userPassword):
        loginURL = 'https://nchu-am.nchu.edu.tw/nidp/idff/sso?sid=0'
        j_spring_security_check = 'https://portal.nchu.edu.tw/portal/j_spring_security_check'
        portal = 'https://portal.nchu.edu.tw/portal'
        payload_userdata = {
            'Ecom_User_ID': userId,
            'Ecom_Password': userPassword,
            'option': 'credential',
            'target': portal
        }
        payload_security_check = {
            'j_username': userId,
            'j_password': userPassword
        }
        self.req.headers.update(self.headers)
        self.rep = self.req.post(loginURL, data=payload_userdata)
        self.rep = self.req.post(
            j_spring_security_check, data=payload_security_check)
        return True if self.rep.status_code == requests.codes.ok else False

    def setCookies(self):
        # 選課主畫面
        self.rep = self.req.get(self.baseLink + 'enro_main')
        # 教務資訊系統
        self.rep = self.req.get(
            self.baseLink + 'acad_subpasschk1?v_subname=enro_stud_list')

    def Global_Education_Preselection(self, courseData, number):
        """
        通識預選            (必需大於等於3堂)
        v_order             課程優先順序
        v_type              一律NM
        v_serial_no       課程號碼
        v_show             修課數
        payload = "
            v_order=123&v_type=NM&v_serial_no=123&
            ...
            v_show=123
        "
        """
        self.setCookies()
        payload_course_data = defaultdict(list)
        payload = ""
        for i in courseData:
            payload_course_data['v_tick'].append(courseData)
        self.req.post(self.baseLink + "gned_bef2", data=payload_course_data)
        for i, d in enumerate(courseData):
            payload += "v_order=" + \
                str(i + 1) + "&v_type=NM&v_serial_no=" + courseData[i] + "&"
        payload += "v_show=" + str(number)
        self.rep = self.req.post(self.baseLink + "gned_bef3", data=payload)
        return True if self.rep.status_code == requests.codes.ok else False

    def Global_Education_Selection(self, courseData):
        """
        通識初選
        v_click             選課號碼
        payload = "
            v_click=123&
            ...
            v_click=453
        "
        """
        self.setCookies()
        self.req.post(self.baseLink + "gned_add2_list")
        payload = defaultdict(list)
        for d in courseData:
            payload['v_click'].append(d)
        self.rep = self.req.post(self.baseLink + "gned_add4_dml", data=payload)
        # pprint(self.rep.text)
        return True if self.rep.status_code == requests.codes.ok else False

    def Other_Selection(self, courseData):
        """
        系上選課、體育、國防、教育學程、其他課程、輸入課號加選
        p_stud_no       學號
        v_tick          選課號碼
        payload = "
            p_stud_no=123&
            v_tick = 13213&
            ...
            v_tick=453
        "
        """
        self.setCookies()
        self.req.post(self.baseLink + "enro_nomo1_list")
        payload = defaultdict(list)
        payload['p_stud_no'].append(self.userId)
        for d in courseData:
            payload['v_tick'].append(d)
        self.rep = self.req.post(
            self.baseLink + "enro_nomo3_dml", data=payload)
        return True if self.rep.status_code == requests.codes.ok else False

    def Direct_Selection(self, courseData):
        """
        輸入課號直選
        p_stud_no       學號
        v_tick          選課號碼
        payload = "
            p_stud_no=123&
            v_tick = 13213&
            ...
            v_tick=453
        "
        """
        self.setCookies()
        self.req.post(self.baseLink + "enro_direct1_list")
        payload = "p_stud_no=" + str(self.userId)
        for d in courseData:
            payload += "&v_tick=" + d
        self.rep = self.req.post(
            self.baseLink + "enro_direct3_dml", data=payload)
        return True if self.rep.status_code == requests.codes.ok else False


class User(object):
    """User description"""

    def __init__(self, id, password):
        super(User, self).__init__()
        self.id = id
        self.password = password
        self.GEP = []
        self.GES = []
        self.OS = []
        self.DS = []

    def setGlobal_Education_Preselection(self, course):
        self.GEP = course

    def setGlobal_Education_Selection(self, course):
        self.GES = course

    def setOther_Selection(self, course):
        self.OS = course

    def setDirect_Selection(self, course):
        self.DS = course


if __name__ == "__main__":
    chaney = User('00000000000', '0000000')
    nancy = User('00000000000', '0000000')

    Users = [chaney, nancy]

    # 大一英文  張   1340
    # 大一英文  阮   1343
    # 大一英文  謝   1339
    # 大一英文  陳   1341
    # 大一英文  林   1342
    # 大一英文  何   1344
    Courses = ['1340', '1343', '1339', '1341', '1342', '1344', '1321']
    for couser in Courses:
        for user in Users:
            i = SnapUpCourses(user)
            i.Global_Education_Selection(couser)
