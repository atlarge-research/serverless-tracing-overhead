import { check, sleep } from 'k6';
import http from 'k6/http';

export const PORTS = {
    python: 5000,
    pythonOtel: 5001,
    go: 5100,
    goOtel: 5101,
};

export const ENDPOINTS = {
    plaintext: "plaintext",
    json: "json",
    db: "db",
    queries: "queries",
    updates: "updates",
}
export const HOST = "http://localhost";

export const TEST_ENDPOINTS = {
    plain: "plain",
    json: "json",
    db: "db",
    queries: "queries",
}

// export let startTime = 0;

export function scenarioHelperConcurrency(concurrencyLevels, duration, appPort, appName, startTimeObj) {
    let scenarios = {}

    concurrencyLevels.forEach((concurrency) => {
        let scenarioName = `${appName}_${concurrency}`;
        scenarios[scenarioName] = {
            executor: 'constant-arrival-rate',
            rate: concurrency,
            timeUnit: '1s',
            duration: `${duration}m`,
            preAllocatedVUs: concurrency,
            maxVUs: concurrency * 2,
            exec: 'test',
            env: { PORT: `${appPort}` },
            startTime: `${startTimeObj.value}m`,
            tags: { testName: `${appName}_${concurrency}` },
        };

        startTimeObj.value += 1;
    });

    return scenarios
}

export function scenarioHelperQueryCount(queryCounts, duration, appPort, appName, startTimeObj, concurrency) {
    let scenarios = {}

    queryCounts.forEach((queryCount) => {
        let scenarioName = `${appName}_${queryCount}`;
        scenarios[scenarioName] = {
            executor: 'constant-arrival-rate',
            rate: concurrency,
            timeUnit: '1s',
            duration: `${duration}m`,
            preAllocatedVUs: concurrency,
            maxVUs: concurrency * 2,
            exec: 'test',
            env: { PORT: `${appPort}`, QUERY_COUNT: `${queryCount}` },
            startTime: `${startTimeObj.value}m`,
            tags: { testName: `${appName}_${queryCount}` },
        };

        startTimeObj.value += 1;
    });

    return scenarios
}