from bs4 import BeautifulSoup
import json


def template_to_json(template_html):
    """
    将模板 HTML 转换为 JSON 格式。
    """

    def parse_tag(tag):
        if not tag.name:
            return None
        return {
            "tag": tag.name,
            "attrs": tag.attrs,
            "children": [
                parse_tag(child)
                for child in tag.find_all(recursive=False)
                if child.name
            ],
        }

    soup = BeautifulSoup(template_html, "lxml")
    root = soup.find()  # 获取根节点
    return parse_tag(root)


def dictCmp(original_dict: dict, template_dict: dict):
    """
    return True only if all the attributes in template_dict is the same as that in original_dict
    """
    for key in template_dict.keys():
        if key not in original_dict.keys():
            return False
        if template_dict[key] != original_dict[key]:
            return False
    return True


def pageParser(original_html, template_json):
    """
    使用栈的方式，根据模板 JSON 修剪原 HTML。
    """
    original_soup = BeautifulSoup(original_html, "lxml")

    def is_tag_match(original_tag, template_node):
        """
        检查原始标签是否匹配模板节点。
        """
        if original_tag.name != template_node["tag"]:
            return False
        if template_node["attrs"]:
            return dictCmp(original_tag.attrs, template_node["attrs"])
        return True

    def process_children(original_parent, template_children):
        """
        使用栈处理子标签。如果模板标签没有子节点，则保留匹配标签的所有子标签。
        """
        stack = [(child, template_children) for child in original_parent.find_all(recursive=False)]
        while stack:
            original_tag, remaining_templates = stack.pop()
            matched_template = None
            for template in remaining_templates:
                if is_tag_match(original_tag, template):
                    matched_template = template
                    break
            if matched_template:
                # 如果匹配且模板标签有子节点，递归处理子标签
                if matched_template["children"]:
                    stack.extend([
                        (child, matched_template["children"])
                        for child in original_tag.find_all(recursive=False)
                    ])
            else:
                # 如果模板没有匹配，删除标签
                original_tag.decompose()

    # 处理顶层标签
    for child in original_soup.find_all(recursive=False):
        # 如果标签匹配模板
        if is_tag_match(child, template_json):
            if template_json["children"]:
                # 如果模板有子标签，递归处理
                process_children(child, template_json["children"])
            else:
                # 如果模板没有子标签，保留该标签的所有子标签
                continue
        else:
            # 如果标签不匹配模板，删除
            child.decompose()

    return original_soup



# 示例用法
if __name__ == "__main__":
    # 读取 HTML 文件
    with open("template.html", "r", encoding="utf-8") as template_file:
        template_html = template_file.read()

    with open("page.html", "r", encoding="utf-8") as original_file:
        original_html = original_file.read()

    # 转换模板为 JSON
    template_json = template_to_json(template_html)

    # 保存模板 JSON 到文件（可选）
    with open("template.json", "w", encoding="utf-8") as json_file:
        json.dump(template_json, json_file, indent=4)

    # # 使用模板 JSON 修剪原 HTML
    # modified_html = pageParser(original_html, template_json)

    # # 写入修改后的 HTML
    # with open("modified.html", "w", encoding="utf-8") as modified_file:
    #     modified_file.write(str(modified_html))

    # print("HTML 页面已基于模板 JSON 高效修剪，并保存为 'modified.html'")
