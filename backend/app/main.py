from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from utils.file_handler import preprocess_file


app = FastAPI()


# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на продакшене нужно будет ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Energy Forecast API is running"}

@app.post("/upload-csv/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Сохраняем загруженный файл во временный путь
        df = pd.read_csv(file.file)

        # Вызываем предобработку файла
        df_processed = preprocess_file(df)

        # Здесь можно сохранить df_processed в память, в файл или БД
        # Пока просто возвращаем форму данных
        return {
            "columns": list(df_processed.columns),
            "rows": df_processed.shape[0],
            "preview": df_processed.head(5).to_dict(orient="records"),
        }
    except Exception as e:
        return {"error": str(e)}
    
