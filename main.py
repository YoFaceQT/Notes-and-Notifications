from typing import List

from fastapi import FastAPI, Depends

from models import TaskSchema, NotificationSchema


app = FastAPI()



@app.post('/tasks')
def add_task(task: TaskSchema):
    tasks.append(task)
    print(tasks)
    return {'Ok': True, 'msg': 'Заметка добавлена'}


@app.get('/tasks', response_model=List[TaskSchema])
def get_task_list():

    return tasks


task1 = TaskSchema(
    id=1,
    name='Учить пайтон',
    description=None
)

task2 = NotificationSchema(
    id=2,
    name='Обед',
    description=None,
    minutes=25
)


tasks = [task1, task2]

# to_dict = task1.model_dump()
# to_json = task1.model_dump_json()

# print(to_dict, type(to_dict))
# print(to_json, type(to_json))
