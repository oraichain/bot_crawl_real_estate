import requests

class Translator:
    def __init__(self, proxies_file):
        self.proxies = self.load_proxies(proxies_file)
    
    def load_proxies(self, proxies_file):
        proxies = []
        with open(proxies_file, 'r') as file:
            for line in file:
                proxies.append(line.strip())
        return proxies
    
    def __call__(self, text, target_language="vi", source_language="en"):
        text = str(text)
        proxy = self.proxies[0] if self.proxies else None
        
        translated_text = ""
        try:
            prefix_url = "https://translate.googleapis.com/translate_a/single?client=gtx&"
            url = prefix_url + f"sl={source_language}&tl={target_language}&dt=t&dt=bd&dj=1&q={text}"
            response = requests.get(url, proxies={"http": proxy})
            
            if response.status_code == 200:
                response_data = response.json()
                for sentence in response_data['sentences']:
                    translated_text += sentence['trans'] + " "
                    
        except Exception as e:
            print(e)
        
        return translated_text.rstrip()


if __name__ == "__main__":
    translator = Translator("data/keys/proxies.txt")
    translation = translator("Hello, how are you?")
    print(translation)
