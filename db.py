import chromadb
import uuid


class VectorStorage:
    def __init__(self, path="./vector_db", name="facts"):
        self.client = chromadb.PersistentClient(path=path)

        try:
            self.collection = self.client.get_collection(name)
        except:
            self.collection = self.client.create_collection(name)
            self._init_data()

    def _init_data(self):
        base_facts = [
            "Доктор Кто - это британский научно-фантастический сериал, который существует с 1963 года и рассказывает о приключениях таинственного путешественника во времени, известного как Доктор.",
            "Регенерация: Впервые введена в 1966 году, когда первый Доктор (Уильям Хартнелл) покинул шоу из-за здоровья, что позволило бесконечно продлевать сериал.",
            "ТАРДИС: Ее форма — не случайность. Она застряла в виде полицейской будки в 1963 году, хотя должна менять маскировку.",
            "Спутники: Они нужны, чтобы объяснять зрителю происходящее и задавать вопросы, подчеркивая человечность Доктора.",
            "Далеки: Главные враги Доктора, созданные Терри Мэйшеном, впервые появились во втором сериале 1963 года.",
            "Утерянные эпизоды: Многие серии 1960-х годов были уничтожены Би-би-си (из-за нехватки места для хранения), и сейчас фанаты ищут их по всему миру.",
            "Секрет имени: Настоящее имя Доктора неизвестно, само название — это вопрос, на который зрители ищут ответ уже более 60 лет."
        ]   
        for fact in base_facts:
            self.add(fact)

    def add(self, text: str):
        self.collection.add(
            documents=[text],
            ids=[str(uuid.uuid4())]
        )

    def search_one(self, query: str) -> str:
        res = self.collection.query(query_texts=[query], n_results=1)

        if not res["documents"] or not res["documents"][0]:
            return ""

        return res["documents"][0][0]

    def get_all(self) -> str:
        data = self.collection.get()
        if not data["documents"]:
            return ""

        return "\n".join(data["documents"])