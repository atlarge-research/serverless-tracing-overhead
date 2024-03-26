import http from "k6/http";
import { sleep, check } from "k6";

export let options = {
    stages: [
        { duration: "30s", target: 100 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 0 },
    ]
}

const HOST = "http://localhost"
const PORT = 5000

export default function () {
    let response = http.get(`${HOST}:${PORT}/plain`)

    check(response, {
        "is status 200": (r) => r.status === 200,
        "is content type text/plain": (r) => r.headers["Content-Type"] === "text/plain",
    });

    sleep(1);
}