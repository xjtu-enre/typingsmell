import request from '@/utils/request';

export function getProjectCoverage(project_id) {
  return request({
    url: `/coverage/${project_id}`,
    method: 'get',
  });
}

export function getCommitCoverage(data) {
  return request({
    url: `/coverage`,
    method: 'post',
    data,
  });
}

export function getCoverage() {
  return request({
    url: `/coverage`,
    method: 'get',
  });
}
