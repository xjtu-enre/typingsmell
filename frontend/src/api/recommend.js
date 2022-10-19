import request from '@/utils/request';

export function getRecommend(data) {
  return request.post('/recommend', data);
}

export function recommendAfterFetch(data) {
  return request.post('/project/import', data);
}
