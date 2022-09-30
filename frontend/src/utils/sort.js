export function sortGraph(dataSet, metric) {
  let temp = dataSet.slice(0);
  return temp.sort(function(a, b) {
    return a[metric] - b[metric];
  });
}
