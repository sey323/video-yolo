API_SERVER_NAME=video-yolo

run:
	docker-compose build
	docker-compose --env-file .env.dev up -d

stop:
	docker stop ${API_SERVER_NAME} 
	docker rm -f ${API_SERVER_NAME}

in:
	docker exec -it ${API_SERVER_NAME} /bin/bash
