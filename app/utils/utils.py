import re 

STATE_PROMPT = """
    Mô phỏng một phiên trò chuyện với việc duy trì lịch sử (state).

    Args:
        history (list): Danh sách các tin nhắn đã trao đổi (mỗi tin nhắn là một dict {'role': 'user'/'model', 'parts': [text]}).
                        Nếu không được cung cấp hoặc là list rỗng, một phiên trò chuyện mới sẽ bắt đầu.

    Returns:
        list: Lịch sử trò chuyện đã được cập nhật sau lượt tương tác này.
    """


def extract_text(s):
    match = re.search(r'text:\s*"([^"]+)"', s)
    if match:
        return match.group(1).encode('utf-8').decode('unicode_escape')
    return None

