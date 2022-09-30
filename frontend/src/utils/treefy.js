export function treefy(baseData) {
  const treeDTO = [];
  if (baseData === []) {
    return [];
  }
  baseData.forEach((item) => {
    const nodeArray = item.split('/');
    const nodeLength = (nodeArray.length - 1).toString();
    let children = treeDTO;
    let currentPathType = 'folder';
    for (const i in nodeArray) {
      if (i === nodeLength) {
        currentPathType = 'file';
      }
      const node = {
        label: nodeArray[i],
        type: currentPathType,
      };
      if (children.length === 0) {
        children.push(node);
      }
      let isExist = false;
      for (const j in children) {
        if (children[j].label === node.label) {
          if (!children[j].children) {
            children[j].children = [];
          }
          children = children[j].children;
          isExist = true;
          break;
        }
      }
      if (!isExist) {
        children.push(node);
        if (!children[children.length - 1].children) {
          children[children.length - 1].children = [];
        }
        children = children[children.length - 1].children;
      }
    }
  });

  return treeDTO;
}
