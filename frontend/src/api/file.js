import request from '@/utils/request';

export function getProjectDir(data) {
  return request.post('/file', data);
}

export function getProjectFile(data) {
  return request({
    url: `/file`,
    method: 'put',
    data,
  });
}
