import request from '@/utils/request';

export function pingServer() {
  return request.get('/ping')
}

export function loginServer(data) {
  return request.post('/login', data);
}

export function registerServer(data) {
  return request.post('/register', data);
}

export function getUserInfo(user_id) {
  return request.get(`/user/${user_id}`);
}

export function modifyUserInfo(user_id, data) {
  return request.put(`/user/${user_id}`, data);
}

export function logout() {
  return request.post('/logout');
}
