import Heading from "@theme/Heading";
import clsx from "clsx";
import type { ReactNode } from "react";
import styles from "./styles.module.css";

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<"svg">>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: "Simplified Access to Mobile Networks",
    Svg: require("@site/static/img/undraw_modern-design_yur1.svg").default,
    description: (
      <>
        GSMA Open Gateway provides universal APIs that offer seamless access to
        mobile operator networks. Developers can easily integrate network
        capabilities without needing deep telecom expertise.
      </>
    ),
  },
  {
    title: "Scalable & Future-Proof API Ecosystem",
    Svg: require("@site/static/img/undraw_stepping-up_4q3b.svg").default,
    description: (
      <>
        Built for ease of use and scalability with a standardized set of
        endpoints, these APIs ensure faster deployment, interoperability, and
        global reach for next-generation services.
      </>
    ),
  },
  {
    title: "Accelerate Digital Transformation",
    Svg: require("@site/static/img/undraw_fast-loading_ae60.svg").default,
    description: (
      <>
        With its streamlined, standardized endpoints, it minimizes integration
        hurdles, enabling developers to rapidly innovate and drive digital
        transformation in today’s 5G and cloud-enabled world.
      </>
    ),
  },
];

function Feature({ title, Svg, description }: FeatureItem) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
