import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import QuizView from "../views/QuizView.vue";
import RecapView from "../views/RecapView.vue";

const routes = [
  { path: "/", component: HomeView }, // Page d'accueil
  { path: "/quiz", component: QuizView }, // Page du quiz
  { path: "/recap", name: "Recap", component: RecapView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
