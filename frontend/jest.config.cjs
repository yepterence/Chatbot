/** @type {import('jest').Config} */
module.exports = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  rootDir: ".",
  setupFilesAfterEnv: ["<rootDir>/src/test/setupTests.ts"],
  testMatch: ["<rootDir>/src/**/*.test.{ts,tsx}"],
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "identity-obj-proxy",
    // react-markdown and its remark/unified dependency chain are ESM-only
    // and pull in a large transitive graph that isn't worth transforming
    // for unit tests; a lightweight mock keeps these tests focused on
    // ChatWindow's own logic instead of the markdown renderer's internals.
    "^react-markdown$": "<rootDir>/src/test/__mocks__/react-markdown.tsx",
  },
  transform: {
    "^.+\\.tsx?$": [
      "ts-jest",
      {
        tsconfig: "<rootDir>/tsconfig.jest.json",
      },
    ],
  },
  clearMocks: true,
};
