import string
import json


class Utils:
    @staticmethod
    def writeToJson(file: str, data: dict) -> str:
        """Menulis data ke dalam file JSON"""
        if not isinstance(data, dict):
            raise ValueError(
                "Data harus berupa dictionary untuk disimpan dalam format JSON."
            )
        with open(file, "w", encoding="utf-8") as json_file:
            json.dump(
                data, json_file, ensure_ascii=False, separators=(",", ":"), indent=4
            )
        return file

    @staticmethod
    def parseResponseGpt(responseGpt: str, originalText: str):
        """Memparsing response GPT untuk mendapatkan JSON, atau mengembalikan teks asli jika gagal"""
        try:
            # Menghapus bagian-bagian yang tidak relevan dan mencoba parsing
            text = responseGpt.replace("Copy code", "").replace("json", "").strip()
            # Memastikan string yang diparsing adalah JSON yang valid
            parsed_data = json.loads(text)
            return parsed_data
        except json.JSONDecodeError as e:
            # Jika parsing JSON gagal, kembalikan teks asli dan log error
            print(f"Error parsing JSON: {e}")
            return originalText
        except Exception as e:
            # Untuk menangani kasus lain yang tidak terduga
            print(f"Error dalam ParseResponseGpt: {e}")
            return originalText

    @staticmethod
    def cleanText(text: str) -> str:
        """Membersihkan teks dari tanda baca dan mengganti spasi dengan underscore"""
        # Menghapus tanda baca dan mengganti spasi ganda dengan satu
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = " ".join(text.split())  # Memastikan tidak ada spasi ganda
        text = "_".join(text.split())  # Mengganti spasi dengan underscore
        return text

    @staticmethod
    def joinText(text: list) -> str:
        if isinstance(text, list):
            return "".join(text)
        return text
