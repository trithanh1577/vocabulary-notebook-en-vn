"""Small server-side client for the Gemini text generation API."""

import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """An API failure with a safe message suitable for the web page."""


def _generate_json(prompt, *, max_output_tokens=1400):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiServiceError(
            "Gemini chưa được cấu hình. Hãy thêm GEMINI_API_KEY vào file .env."
        )

    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
    allowed_model_characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    if not model or any(character not in allowed_model_characters for character in model):
        raise GeminiServiceError("Cấu hình tên mô hình Gemini không hợp lệ.")

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.35,
            "maxOutputTokens": max_output_tokens,
        },
    }
    request = Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            response_data = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        logger.warning("Gemini API returned HTTP %s", error.code)
        if error.code in {400, 401, 403}:
            raise GeminiServiceError(
                "Gemini không chấp nhận API key. Hãy kiểm tra key mới và quyền dùng Gemini API."
            ) from None
        if error.code == 429:
            raise GeminiServiceError(
                "Gemini đang quá tải hoặc đã hết hạn mức. Hãy thử lại sau."
            ) from None
        raise GeminiServiceError(
            "Gemini tạm thời không xử lý được yêu cầu. Hãy thử lại sau."
        ) from None
    except (URLError, TimeoutError, OSError):
        logger.warning("Could not reach Gemini API")
        raise GeminiServiceError(
            "Không kết nối được Gemini. Kiểm tra mạng rồi thử lại."
        ) from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.warning("Gemini API returned an invalid response")
        raise GeminiServiceError(
            "Gemini trả về phản hồi không hợp lệ. Hãy thử lại."
        ) from None

    try:
        parts = response_data["candidates"][0]["content"]["parts"]
        response_text = "".join(part.get("text", "") for part in parts).strip()
        result = json.loads(response_text)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        raise GeminiServiceError(
            "Gemini chưa tạo được nội dung phù hợp. Hãy thử lại."
        ) from None

    return result


def _clean_word(item):
    if not isinstance(item, dict):
        return None
    cleaned = {
        "word": str(item.get("word", "")).strip()[:120],
        "part_of_speech": str(item.get("part_of_speech", "")).strip()[:60],
        "meaning_vi": str(item.get("meaning_vi", "")).strip(),
        "example_sentence": str(item.get("example_sentence", "")).strip(),
        "usage_note": str(item.get("usage_note", "")).strip(),
    }
    if not cleaned["word"] or not cleaned["meaning_vi"]:
        return None
    return cleaned


def generate_new_vocabulary(count=8):
    prompt = f"""Create exactly {count} useful English vocabulary entries for a Vietnamese learner at A2-B2 level.
Return one JSON object with a `words` array. Each entry must have these string fields:
`word`, `part_of_speech`, `meaning_vi`, `example_sentence`, `usage_note`.
Use a short, natural English example sentence. Write the meaning and usage note in Vietnamese.
Choose distinct, common words. Do not include markdown or any text outside the JSON object."""
    result = _generate_json(prompt, max_output_tokens=1800)
    items = result.get("words") if isinstance(result, dict) else result
    if not isinstance(items, list):
        raise GeminiServiceError("Gemini chưa tạo được danh sách từ. Hãy thử lại.")

    words = []
    seen = set()
    for item in items:
        word = _clean_word(item)
        if not word or word["word"].casefold() in seen:
            continue
        seen.add(word["word"].casefold())
        words.append(word)
    if not words:
        raise GeminiServiceError("Gemini chưa tạo được danh sách từ. Hãy thử lại.")
    return words


def generate_word_examples(word, meaning_vi, part_of_speech=""):
    prompt = f"""For this English vocabulary entry, return one JSON object with exactly three string fields:
`example_sentence` (a short natural English sentence using the word),
`usage_note` (a concise Vietnamese usage explanation), and `part_of_speech`.
Word: {word}
Vietnamese meaning: {meaning_vi}
Part of speech if known: {part_of_speech or 'not provided'}
Return only the JSON object, without markdown."""
    result = _generate_json(prompt, max_output_tokens=500)
    if not isinstance(result, dict):
        raise GeminiServiceError("Gemini chưa tạo được gợi ý. Hãy thử lại.")

    example = str(result.get("example_sentence", "")).strip()
    usage = str(result.get("usage_note", "")).strip()
    generated_pos = str(result.get("part_of_speech", "")).strip()[:60]
    if not example or not usage:
        raise GeminiServiceError("Gemini chưa tạo đủ gợi ý. Hãy thử lại.")
    return {
        "example_sentence": example,
        "usage_note": usage,
        "part_of_speech": generated_pos,
    }
