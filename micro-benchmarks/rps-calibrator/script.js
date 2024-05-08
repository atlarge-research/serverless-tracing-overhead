import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    constant_request_rate: {
      executor: 'constant-arrival-rate',
      rate: __ENV.RPS,
      timeUnit: `${__ENV.TIMEUNIT}`,
      duration: `${__ENV.DURATION}s`,
      preAllocatedVUs: 500,
      maxVUs: 2000,
      gracefulStop: '15s'
    },
  },
};

export default function () {
    let response = http.get(__ENV.URL);
    check(response, {
        'is status 200': (r) => r.status === 200,
    });
}
