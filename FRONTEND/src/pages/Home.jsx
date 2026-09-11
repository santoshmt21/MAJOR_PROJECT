import cowImage from "../cow.jpg";
import { HERO_STATS } from "../data/breeds";
import styles from "./Home.module.scss";

export default function Home() {
  return (
    <section className={styles.hero}>
      <div className={styles.overlay} />
      <div className={styles.content}>
        <div className={styles.eyebrow}>AI-Powered Cattle Intelligence</div>
        <h1 className={styles.title}>
          Know Your Herd.<br />
          <span>Grow Your Farm.</span>
        </h1>
        <p className={styles.description}>
          Every animal tells a story. Every farmer deserves the tools to listen.
        </p>
        <p className={styles.quote}>&quot;Every herd counts. Every farmer matters.&quot;</p>
        <div className={styles.stats}>
          {HERO_STATS.map((stat) => (
            <div key={stat.label} className={styles.statCard}>
              <div className={styles.statValue}>{stat.value}</div>
              <div className={styles.statLabel}>{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
