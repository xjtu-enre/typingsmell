import { createRouter, createWebHashHistory } from 'vue-router';
import Home from '../views/Home';
import Projects from '../views/Projects';
import Coverage from '../views/Coverage';
import Usage from '../views/Usage';
import Static from '../views/Static';
import Recommend from '../views/Recommend';
import Commit from '../views/Commit';

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
  },
  {
    path: '/projects',
    name: 'projects',
    component: Projects,
  },
  {
    path: '/coverage',
    name: 'coverage',
    component: Coverage,
  },
  {
    path: '/usage',
    name: 'usage',
    component: Usage,
  },
  {
    path: '/commit-cov',
    name: 'commit-coverage',
    component: Commit,
  },
  {
    path: '/recommend',
    name: 'recommend',
    component: Recommend,
  },
  {
    path: '/static',
    name: 'static',
    component: Static,
  },
  {
    path: '/404',
    component: () => import('../views/404/index'),
    name: '404',
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
