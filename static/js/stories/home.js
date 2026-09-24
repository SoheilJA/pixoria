/* داستان خانه — پس‌زمینه‌ی سیارات (لندینگ ۵) + کنسول آرکید.
   داستان موشک حذف شد. */
import { $ } from "../core/utils.js";
import { initThreeBackground } from "../engine/background3d.js";

export function initHomeStory() {
  initThreeBackground();
  if ($("#arcade")) {
    import("../arcade/console.js").then((m) => m.default.init());
  }
}
initHomeStory();
