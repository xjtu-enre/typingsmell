import request from '@/utils/request';

export function getProjectUsage(project_id) {
  return request({
    url: `/usage/${project_id}`,
    method: 'get',
  });
}

export function getUsage() {
  return request({
    url: `/usage`,
    method: 'get',
  });
}