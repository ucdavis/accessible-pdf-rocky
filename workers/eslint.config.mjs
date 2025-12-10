import js from "@eslint/js";
import tsPlugin from "@typescript-eslint/eslint-plugin";
import tsParser from "@typescript-eslint/parser";

export default [
  js.configs.recommended,
  {
    files: ["**/*.ts"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
      },
      globals: {
        // Cloudflare Workers globals
        Request: "readonly",
        Response: "readonly",
        Headers: "readonly",
        crypto: "readonly",
        File: "readonly",
        URL: "readonly",
        console: "readonly",
        // Cloudflare Workers types
        R2Bucket: "readonly",
        Queue: "readonly",
        Env: "readonly",
        D1Database: "readonly",
        ExecutionContext: "readonly",
        ScheduledEvent: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
    },
  },
  {
    ignores: ["node_modules/**", "dist/**"],
  },
];
