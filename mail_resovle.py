from lxml import etree
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

class MailResovle:
    def resovle_to_mail(self, msg_content) -> dict:
        msg = Parser().parsestr(msg_content) # 稍后解析出邮件:
        if self.__check_mail(msg) == False:
            return {}
        order_type = self.__train_type(msg)
        order_id, order_info = self.__mail_content(msg)
        if len(order_id) > 0 and len(order_type) > 0 or len(order_info) > 0:
            return {"order_id": order_id, "order_type": order_type, "order_info": order_info}
        else:
            return {}

    def __mail_content(self, msg):
        if msg.is_multipart():
            parts = msg.get_payload()
            if len(parts) > 0:
                return self.__mail_content_html(parts[0])
        return '',''

    def __mail_content_html(self, msg):
        content_type = msg.get_content_type()
        if  'text/html' in content_type:
            charset = self.__content_charset(msg)
            if charset:
                content = msg.get_payload(decode=True).decode(charset)
                return self.__get_order_info(content)
        return '',''

    def __get_order_info(self, content_html):
        order_id = ''
        order_info_str = ''
        etree_html = etree.HTML(content_html) # 构造 entree.HTML 对象
        order_id_xpath = '//td/div[2]/span/text()' # 设置目标 xpath 值，注意 xpath & text() 的拼接
        order_id_result = etree_html.xpath(order_id_xpath) # 得到目标数据
        if len(order_id_result) > 0:
            order_id = order_id_result[0]
        order_info_result = etree_html.xpath('//td/div/div[1]/text()') 
        if len(order_info_result) > 0:
            order_info_str = order_info_result[0].strip()
        return order_id, order_info_str

    def __train_type(self, msg):
        subject = self.__decode_str(msg.get('Subject', ''))
        if "支付通知" in subject:
            return 'insert'
        elif "退票通知" in subject:
            return 'delete'
        elif "改签通知" in subject:
            return 'modify'
        return ''

    def __content_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()
        return charset

    def __decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def __check_mail(self, msg) -> bool:
        _, from_address = parseaddr(msg.get('From', ''))
        return '12306@rails.com.cn' in from_address
