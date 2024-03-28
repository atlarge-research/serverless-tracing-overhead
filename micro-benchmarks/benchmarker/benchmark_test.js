import http from 'k6/http'
import { check } from "k6";


export const options = {
    scenarios: {
        plaintext_constant: {
            executor: 'constant-vus',
            exec: 'plaintext',
            vus: 10,
            duration: '30s',
            gracefulStop: '0s',
            tags: { test: 'plaintext_constant' },
        },
        plaintext: {
            executor: 'per-vu-iterations',
            exec: 'plaintext',
            vus: 100,
            iterations: 1000,
            maxDuration: '30m',
            startTime: '1m',
            tags: { test: 'plaintext_per_vu' },
        },
    }
}

const HOST = "http://localhost"
const PYTHON_PORT = 5000
const GO_PORT = 5100

export function plaintext() {
    let response = http.get(`${HOST}:${PYTHON_PORT}/plain`)

    // check(response, {
    //     "is status 200": (r) => r.status === 200,
    //     "is content type text/plain": (r) => r.headers["Content-Type"] === "text/plain",
    // });
}