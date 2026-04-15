export const AUTH_STORAGE_KEY = "pm-authenticated";
export const AUTH_USERNAME = "user";
export const AUTH_PASSWORD = "password";

export const isValidCredentials = (username: string, password: string): boolean => {
  return username === AUTH_USERNAME && password === AUTH_PASSWORD;
};
