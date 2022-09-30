import request from '@/utils/request';

export function getProjectPattern(project_id) {
  return request({
    url: `/pattern/${project_id}`,
    method: 'get',
  });
}

export function getPattern() {
  return request({
    url: `/pattern`,
    method: 'get',
  });
}