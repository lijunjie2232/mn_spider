from bs4 import BeautifulSoup
import json

def html_to_json(soup):
    if soup.name is None:
        return None

    element = {
        "tag": soup.name,
        "attrs": soup.attrs,
        "children": []
    }

    for child in soup.children:
        child_json = html_to_json(child)
        if child_json:
            element["children"].append(child_json)

    return element

def convert_html_to_json(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # 由于BeautifulSoup会自动添加<html>, <head>, <body>标签，我们需要从<body>开始
    body_tag = soup.find('body')
    if body_tag:
        return html_to_json(body_tag)
    else:
        return html_to_json(soup)

if __name__ == "__main__":
    with open("template.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    json_structure = convert_html_to_json(html_content)

    # 将JSON结构写入文件
    with open("template.json", "w", encoding="utf-8") as f:
        json.dump(json_structure, f, ensure_ascii=False, indent=2)

    print("转换完成，结果已保存到template.json")