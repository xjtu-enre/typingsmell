import request from '@/utils/request';

export function uploadProject(data) {
  return request.post('/project/upload', data);
}

export function addProject(data) {
  return request.post('/project', data);
}

export function getProjectList(params) {
  return request({
    url: '/project',
    method: 'get',
    params,
  });
}
