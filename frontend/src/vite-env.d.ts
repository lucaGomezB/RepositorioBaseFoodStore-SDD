/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_MP_PUBLIC_KEY: string;
  readonly VITE_LOGIN_USER: string;
  readonly VITE_LOGIN_PASS: string;
  readonly VITE_ENV: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}