#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> str tools
@@..> package utils
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from typing import Generator
# @@..> StrAct
from re import findall, S as ReS, compile as ReCompile, error as ReError
from gzip import GzipFile
from io import BytesIO
from decimal import Decimal
# @@..> UrlAct
from validators import url as ValiUrl
from urllib.parse import urlencode, parse_qs, urlparse
from urllib.parse import quote_plus, unquote_plus
# @@..> DomAct
from lxml import etree
from cssselect.parser import SelectorSyntaxError
# @@..> EncryptAct
# from Crypto.Cipher import AES
from base64 import b64encode, b64decode, decodebytes
from pyDes import des, ECB
import hashlib
import zlib


#######################################################################################
# @@... to be continue
class StrAct:
    """
    [about string object]
    """
    logger: any = False

    @classmethod
    def parse_regex(cls, source_data: str = "", regex_syntax: str = "") -> Generator:
        """
        [regex match the string]

        Args:
            source_data (str, optional): [nothing.]. Defaults to nothing.
            regex_syntax (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            Generator: [nothing.]
        """
        if isinstance(source_data, str) and isinstance(regex_syntax, str):
            try:
                source_data = findall(regex_syntax, source_data, ReS)
                if source_data:
                    for i in source_data:
                        yield i
                else:
                    return (x for x in range(0))
            except ReError:
                cls.logger.info(f"解析Regex对象失败(*>﹏<*)【{regex_syntax}】")
                return (x for x in range(0))
        else:
            cls.logger.info("解析Regex对象失败(*>﹏<*)【type】")
            return (x for x in range(0))

    @classmethod
    def parse_replace(cls, source_data: str = "", regex_syntax: str = "",
                      replaced_string: str = "") -> str:
        """
        [replace the string]

        Args:
            source_data (str, optional): [nothing.]. Defaults to nothing.
            regex_syntax (str, optional): [nothing.]. Defaults to nothing.
            replaced_string (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            str: [nothing.]
        """
        if isinstance(source_data, str) and isinstance(regex_syntax, str) \
                and isinstance(replaced_string, str):
            try:
                comp_regex = ReCompile(regex_syntax, ReS)
                source_data = comp_regex.sub(replaced_string, source_data)
                return source_data
            except ReError:
                cls.logger.info(f"解析Replace对象失败(*>﹏<*)【{regex_syntax}】")
                return ""
        else:
            cls.logger.info("解析Replace对象失败(*>﹏<*)【type】")
            return ""

    @classmethod
    def format_clear(cls, source_data: str = "", is_separate: bool = False) -> str:
        """
        [clear the string]

        Args:
            source_data (str, optional): [nothing.]. Defaults to nothing.
            is_separate (bool, optional): [if it has a space]. Defaults to False.

        Returns:
            str: [nothing.]
        """
        if isinstance(is_separate, bool):
            if is_separate:
                source_data = cls.parse_replace(source_data, r"\r|\n|\t", "")
                return cls.parse_replace(source_data, r"\s+", " ")
            else:
                return cls.parse_replace(source_data, r"\r|\n|\t|\s+", "")
        else:
            cls.logger.info("格式Clear对象失败(*>﹏<*)【type】")
            return cls.parse_replace(source_data, r"\r|\n|\t|\s+", "")

    @classmethod
    def format_html(cls, source_data: str = "") -> str:
        """
        [clear the html tags]

        Args:
            source_data (str, optional): [html string]. Defaults to nothing.

        Returns:
            str: [nothing.]
        """
        return cls.parse_replace(source_data, r"<[^>]+>", " ")

    @classmethod
    def parse_integer(cls, source_data: any = None) -> Generator:
        """
        [turn into int]

        Args:
            source_data (any, optional): [int/float/str]. Defaults to None.

        Returns:
            Generator: [nothing.]
        """
        if isinstance(source_data, (int, float, Decimal)):
            yield int(source_data)
        elif isinstance(source_data, str):
            source_data = cls.parse_regex(source_data, "\\d+")
            for i in source_data:
                yield int(i)
        else:
            cls.logger.info("解析Integer对象失败(*>﹏<*)【type】")
            return (x for x in range(0))

    @classmethod
    def parse_decimal(cls, source_data: any = None, decimal_num: int = 2) -> Generator:
        """
        [turn into float]

        Args:
            source_data (any, optional): [int/float/str]. Defaults to None.
            decimal_num (int, optional): [num of decimals]. Defaults to 2.

        Returns:
            Generator: [nothing.]
        """
        if not isinstance(decimal_num, int):
            cls.logger.info("解析Decimal对象失败(*>﹏<*)【type】")
            return (x for x in range(0))

        if isinstance(source_data, (int, float, Decimal)):
            yield round(float(source_data), decimal_num)
        elif isinstance(source_data, str):
            source_data = cls.parse_regex(source_data, "\\d+.\\d+")
            for i in source_data:
                yield round(float(i), decimal_num)
        else:
            cls.logger.info("解析Decimal对象失败(*>﹏<*)【type】")
            return (x for x in range(0))

    @classmethod
    def parse_millions(cls, source_data: str = "") -> any:
        """
        [turn millions into number]

        Args:
            source_data (any, optional): [int/float/str]. Defaults to None.

        Returns:
            any: [nothing.]
        """
        if not isinstance(source_data, str):
            cls.logger.info("解析Millions对象失败(*>﹏<*)【type】")
            return 0

        units = ["w", "W", "万", "亿"]
        result = 0

        if any(u in source_data for u in units):
            if "." in source_data:
                result_gen = cls.parse_decimal(source_data)
            else:
                result_gen = cls.parse_integer(source_data)

            for i in result_gen:
                result = i
                break
            if "亿" in source_data:
                result *= 100000000
            else:
                result *= 10000
            return result

        else:
            if "." in source_data:
                result_gen = cls.parse_decimal(source_data)
            else:
                result_gen = cls.parse_integer(source_data)
            for i in result_gen:
                result = i
                break

            return result

    @classmethod
    def format_gzip(cls, source_data: str = "") -> bytes:
        """
        [put gzip buff]

        Args:
            source_data (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            bytes: [nothing.]
        """
        if isinstance(source_data, str):
            buf = BytesIO()
            with GzipFile(mode='wb', fileobj=buf) as f:
                gzip_value = str.encode(source_data, encoding='utf-8')
                f.write(gzip_value)
            return buf.getvalue()
        else:
            cls.logger.info("格式Gzip对象失败(*>﹏<*)【type】")
            return b""

    @classmethod
    def parse_gzip(cls, source_data: bytes = b"") -> str:
        """
        [get gzip buff]

        Args:
            source_data (bytes, optional): [nothing.]. Defaults to nothing.

        Returns:
            str: [nothing.]
        """
        if isinstance(source_data, bytes):
            buf = BytesIO(source_data)
            with GzipFile(fileobj=buf) as f:
                content = f.read()
            return content.decode('utf-8')
        else:
            cls.logger.info("解析Gzip对象失败(*>﹏<*)【type】")
            return ""

    @classmethod
    def parse_include(cls, source_data: str = "", source_set: set = None) -> bool:
        """
        [check if string in the set]

        Args:
            source_data (str, optional): [nothing.]. Defaults to nothing.
            source_set (set, optional): [nothing.]. Defaults to None.

        Returns:
            bool: [nothing.]
        """
        if isinstance(source_data, str) and isinstance(source_set, set) \
                and all(isinstance(s, str) for s in source_set):
            # @@..! s in source_data
            if any(s in source_data for s in source_set):
                return True
            else:
                return False
        else:
            cls.logger.info("解析Include包含失败(*>﹏<*)【type】")
            return False

    # def format_num(cls, num: int = 0) -> str:
    #     """ [parse string to json]
    #
    #     Args:
    #         source_data (any, optional): [int/float]. Defaults to None.
    #         decimal_num (int, optional): [int/float]. Defaults to 2.
    #
    #     Returns:
    #         float: [description]
    #     """
    #     def strofsize(num, level):
    #         if level >= 2:
    #             return num, level
    #         elif num >= 10000:
    #             num /= 10000
    #             level += 1
    #             return strofsize(num, level)
    #         else:
    #             return num, level
    #
    #     units = ['', '万', '亿']
    #     num, level = strofsize(num, 0)
    #     if level > len(units):
    #         level -= 1
    #     return f'{round(num, 2)}{units[level]}'


#######################################################################################
# @@... to be continue
class UrlAct:
    """
    [about url object]
    """
    logger: any = False

    @classmethod
    def parse_check(cls, source_data: str = "") -> bool:
        """
        [check url if right or not]

        Args:
            source_data (str, optional): [url address]. Defaults to nothing.

        Returns:
            bool: [nothing.]
        """
        if isinstance(source_data, str):
            if ValiUrl(source_data):
                return True
            else:
                cls.logger.info("检查Url规则失败(*>﹏<*)【check】")
                return False
        else:
            cls.logger.info("检查Url规则失败(*>﹏<*)【type】")
            return False

    @classmethod
    def parse_url(cls, source_data: str = "") -> tuple:
        """
        [parse url to params]

        Args:
            source_data (str, optional): [url address]. Defaults to nothing.

        Returns:
            tuple: [(str, str, str, dict)]
        """
        if cls.parse_check(source_data):
            url_head = urlparse(source_data).scheme
            url_domain = urlparse(source_data).netloc
            url_path = urlparse(source_data).path
            url_query = urlparse(source_data).query
            url_dict = parse_qs(url_query)
            return url_head, url_domain, url_path, url_dict
        else:
            return "", "", "", {}

    @classmethod
    def format_url(cls, source_data: dict = None) -> str:
        """
        [format params to url]

        Args:
            source_data (dict, optional): [key/value]. Defaults to None.

        Returns:
            str: [url string]
        """
        if isinstance(source_data, dict):
            return urlencode(source_data, encoding="utf-8")
        else:
            cls.logger.info("格式Url字串失败(*>﹏<*)【type】")
            return ""

    @classmethod
    def parse_quote(cls, source_data: str = "") -> str:
        """
        [parse quote string to normal string]

        Args:
            source_data (str, optional): [quote string]. Defaults to nothing.

        Returns:
            str: [normal string]
        """
        if isinstance(source_data, str):
            return unquote_plus(source_data)
        else:
            cls.logger.info("解析Quote字串失败(*>﹏<*)【type】")
            return ""

    @classmethod
    def format_quote(cls, source_data: str = "") -> str:
        """
        [format normal string to quote string]

        Args:
            source_data (str, optional): [normal string]. Defaults to nothing.

        Returns:
            str: [quote string]
        """
        if isinstance(source_data, str):
            return quote_plus(source_data)
        else:
            cls.logger.info("格式Quote字串失败(*>﹏<*)【type】")
            return ""


#######################################################################################
# @@... to be continue
class DomAct:
    """
    [about dom object]
    """
    logger: any = False

    @classmethod
    def parse_dom(cls, source_data: str = "") -> etree._Element:
        """
        [parse html string to dom object]

        Args:
            source_data (str, optional): [html string]. Defaults to nothing.

        Returns:
            etree._Element: [nothing.]
        """
        if not isinstance(source_data, str):
            source_data = str(source_data)
        html_dom = etree.HTML(
            source_data, parser=etree.HTMLPullParser(encoding="utf-8"))
        return html_dom

    @classmethod
    def parse_xpath(cls, html: etree._Element = None, syntax: str = "",
                    has_tag: bool = False) -> Generator:
        """
        [parse element if xpath is validate]

        Args:
            html (etree._Element, optional): [dom object]. Defaults to None.
            syntax (str, optional): [xpath syntax]. Defaults to nothing.
            has_tag (bool, optional): [return if has tag string]. Defaults to False.

        Returns:
            Generator: [nothing.]
        """
        if isinstance(html, etree._Element) and isinstance(syntax, str) \
                and isinstance(has_tag, bool) and html is not None:
            pass
        else:
            cls.logger.info("解析Xpath对象失败(*>﹏<*)【type】")
            return (x for x in range(0))

        try:
            elements = html.xpath(syntax)
            if not elements:
                return (x for x in range(0))
            else:
                if has_tag:
                    for i in elements:
                        if isinstance(i, etree._Element):
                            return_data = etree.tostring(
                                i, encoding="utf-8", method='html')
                            yield return_data.decode('utf-8')
                        else:
                            cls.logger.info("解析Xpath对象失败(*>﹏<*)【tags】")
                            return (x for x in range(0))
                else:
                    for i in elements:
                        if isinstance(i, etree._ElementUnicodeResult):
                            yield str(i)
                        else:
                            cls.logger.info("解析Xpath对象失败(*>﹏<*)【value】")
                            return (x for x in range(0))

        except TypeError:
            cls.logger.info(f"解析Xpath对象失败(*>﹏<*)【{syntax}/{has_tag}】")
            return (x for x in range(0))
        except etree.XPathEvalError:
            cls.logger.info(f"解析Xpath对象失败(*>﹏<*)【{syntax}/{has_tag}】")
            return (x for x in range(0))

    @classmethod
    def parse_selector(cls, html: etree._Element = None, syntax: str = "",
                       attrib_name: str = "text", has_tag: bool = False) -> Generator:
        """
        [parse element if css is validate]

        Args:
            html (etree._Element, optional): [dom object]. Defaults to None.
            syntax (str, optional): [css syntax]. Defaults to nothing.
            attrib_name (str, optional): [nothing.]. Defaults to text.
            has_tag (bool, optional): [return if has tag string]. Defaults to False.

        Returns:
            Generator: [nothing.]
        """
        if isinstance(html, etree._Element) and isinstance(syntax, str) \
                and isinstance(attrib_name, str) and isinstance(has_tag, bool) \
                and html is not None:
            pass
        else:
            cls.logger.info("解析Css对象失败(*>﹏<*)【type】")
            return (x for x in range(0))

        try:
            elements = html.cssselect(syntax)
            if not elements:
                return (x for x in range(0))
            else:
                if has_tag:
                    for i in elements:
                        if isinstance(i, etree._Element):
                            return_data = etree.tostring(
                                i, encoding="utf-8", method='html')
                            yield return_data.decode('utf-8')
                        else:
                            cls.logger.info("解析Css对象失败(*>﹏<*)【tags】")
                            return (x for x in range(0))
                else:
                    for i in elements:
                        if isinstance(i, etree._Element):
                            if attrib_name == "text":
                                if i.text is None:
                                    yield ""
                                else:
                                    yield i.text
                            else:
                                elem_attr = i.attrib
                                yield elem_attr.get(attrib_name, "")
                        else:
                            cls.logger.info("解析Css对象失败(*>﹏<*)【value】")
                            return (x for x in range(0))

        except TypeError:
            cls.logger.info(
                f"解析Css对象失败(*>﹏<*)【{syntax}/{attrib_name}/{has_tag}】")
            return (x for x in range(0))
        except SelectorSyntaxError:
            cls.logger.info(
                f"解析Css对象失败(*>﹏<*)【{syntax}/{attrib_name}/{has_tag}】")
            return (x for x in range(0))


#######################################################################################
# @@... to be continue
class EncryptAct:
    """
    [about encryption Object]
    """
    logger: any = False

    @classmethod
    def format_md5(cls, source_data: str = "") -> str:
        """
        [turn into the md5 string]

        Args:
            source_data (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            str: [nothing.]
        """
        if isinstance(source_data, str):
            md = hashlib.md5()
            md.update(source_data.encode("utf-8"))
            return md.hexdigest()
        else:
            print(source_data)
            cls.logger.info("格式MD5字串失败(*>﹏<*)【type】")
            return ""

    @classmethod
    def format_crc32(cls, source_data: str = "") -> int:
        """
        [turn into the crc32 string]

        Args:
            source_data (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            int: [nothing.]
        """
        if isinstance(source_data, str):
            return zlib.crc32(source_data.encode("utf-8"))
        else:
            cls.logger.info("格式CRC32字串失败(*>﹏<*)【type】")
            return 0

    @classmethod
    def format_des(cls, source_data: any = None, source_key: str = "",
                   is_encrypt: bool = True) -> str:
        """
        [turn into the des string]

        Args:
            source_data (any, optional): [nothing.]. Defaults to None.
            source_key (str, optional): [nothing.]. Defaults to nothing.
            is_encrypt (bool, optional): [nothing.]. Defaults to True.

        Returns:
            str: [nothing.]
        """
        try:
            des_obj = des(source_key.encode(), mode=ECB)
            if is_encrypt:
                # padding
                block_size = 8
                content = str(source_data).encode()
                while len(content) % block_size:
                    content += b'\0'

                return b64encode(des_obj.encrypt(content)).decode('utf-8')
            else:
                # decrypt
                return des_obj.decrypt(b64decode(str(source_data))).decode('utf-8')
        except Exception as ex:
            cls.logger.info(f"格式DES字串失败(*>﹏<*)【{ex}】")
            return ""

    # def format_sha1(self, source_key: str = "") -> str:
    #     """ [crc32]

    #     Args:
    #         source_data (str, optional):
    #         [self.password_key: str = "88ios99android66"]. Defaults to "".

    #     Returns:
    #         int: [description]
    #     """
    #     if type(source_key) is not str:
    #         self.logger.info(f"加密字符参数有误(*>﹏<*)【SHA1】【{source_key}】")
    #         return ""

    #     key_bytes = source_key.encode('utf-8')
    #     signature = hashlib.sha1(key_bytes).digest()
    #     signature = hashlib.sha1(signature).digest()
    #     key_hex = signature.hex()
    #     key_hex = key_hex.upper()[:32]
    #     return key_hex

    # def format_aes(self, source_key: str = "", source_string: str = "") -> str:
    #     """AES encryption. AES加密。

    #     Args:
    #         source_key (str): The source key. 来源关键值。
    #         source_string (str): The source string. 来源数据。

    #     Returns:
    #         str
    #     """
    #     try:
    #         key_hex = bytes.fromhex(source_key)
    #         crypto = AES.new(key_hex, AES.MODE_ECB)
    #         padding_value = source_string + \
    #             (AES.block_size - len(source_string) % AES.block_size) \
    #             * chr(AES.block_size - len(source_string) % AES.block_size)
    #         padding_value = padding_value.encode("utf-8")
    #         cipher_text = crypto.encrypt(padding_value)
    #         cipher_text = b64encode(cipher_text)
    #         cipher_text = cipher_text.decode('utf-8')
    #     except Exception as ex:
    #         self.logger.info(f"加密字符程序失败(*>﹏<*)【AES】【{source_string}】")
    #         self.logger.info(f"加密字符失败原因(*>﹏<*)【{ex}】")
    #         return ""
    #     else:
    #         return cipher_text

    # def parse_aes(self, source_key: str = "", source_string: str = "") -> str:
    #     """AES decryption. AES解密。

    #     Args:
    #         source_key (str): The source key. 来源关键值。
    #         source_string (str): The source string. 来源数据。

    #     Returns:
    #         str
    #     """
    #     try:
    #         key_hex = bytes.fromhex(source_key)
    #         crypto = AES.new(key_hex, AES.MODE_ECB)
    #         base64_decrypted = decodebytes(source_string.encode(encoding='utf-8'))
    #         cipher_text = crypto.decrypt(base64_decrypted)
    #         padding_value = cipher_text[:-ord(cipher_text[len(cipher_text) - 1:])]
    #         padding_value = padding_value.decode('utf-8')
    #     except Exception as ex:
    #         self.logger.info(f"解密字符程序失败(*>﹏<*)【AES】【{source_string}】")
    #         self.logger.info(f"解密字符失败原因(*>﹏<*)【{ex}】")
    #         return ""
    #     else:
    #         return padding_value
