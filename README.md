## Asynchronous Tasks with FastAPI and Celery

This project uses [FastAPI](https://github.com/tiangolo/fastapi), [Celery](https://github.com/celery/celery), and [Docker](https://www.docker.com/) to handle background processes.

## Want to use this project?

Spin up the containers:

```sh
docker-compose up -d --build
```

Open your browser to [http://localhost:8004](http://localhost:8004) to view the app or to [http://localhost:5556](http://localhost:5556) to view the Flower dashboard.

Trigger a new task:

```sh
curl http://localhost:8004/tasks -H "Content-Type: application/json" --data '{"uri": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

Check the status:

```sh
curl http://localhost:8004/tasks/${TASK_ID}
```
## Credits

This project was inspired by this [post](https://testdriven.io/blog/fastapi-and-celery/) by [testdrivenio](https://github.com/testdrivenio).
