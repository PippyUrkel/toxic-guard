import { Service } from "../cards/Service";
import { Container } from "../shared/Container";
import { Paragraph } from "../shared/Paragraph";
import { Title } from "../shared/Title";

export const Services = () => {
  const components = [
    {
      title: "Model (BiLSTM)",
      description: "The neural network core responsible for classifying text into multiple toxicity categories.",
      icon: "🧠",
    },
    {
      title: "Tokenizer & Vectorizer",
      description: "Converts raw text into machine-understandable numerical form for accurate processing.",
      icon: "🧾",
    },
    {
      title: "Flask API",
      description: "Handles prediction requests from the frontend and communicates with the trained model.",
      icon: "💾",
    },
    {
      title: "React Frontend",
      description: "Interactive interface where users input comments and view detailed analysis results.",
      icon: "⚡",
    },
    {
      title: "TensorFlow Backend",
      description: "Executes the BiLSTM model efficiently for accurate real-time predictions.",
      icon: "🧰",
    },
    {
      title: "CORS Enabled Communication",
      description: "Ensures secure and smooth data transfer between the Flask backend and React frontend.",
      icon: "🔐",
    },
  ];

  return (
    <section id="system-components">
      <Container className="space-y-10 md:space-y-12">
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <Title> System Components </Title>
          <Paragraph>
            Explore the key components that make our Toxic Comment Detection System efficient, secure, and scalable.
          </Paragraph>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {components.map((item, key) => (
            <Service
              key={key}
              title={`${item.title}`}
              description={item.description}
              icon={item.icon}
            />
          ))}
        </div>
      </Container>
    </section>
  );
};
