import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: __ENV.RPS,
      timeUnit: '1s',
      duration: `${__ENV.DURATION}s`,
      preAllocatedVUs: 100,
      maxVUs: 2000,
    },
  },
};

export default function () {
    http.get(__ENV.URL);
    sleep(1);
}
