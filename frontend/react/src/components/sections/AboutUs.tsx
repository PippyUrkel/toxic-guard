import { Info } from "../cards/Info";
import { Container } from "../shared/Container";
import { Paragraph } from "../shared/Paragraph";
import { Title } from "../shared/Title";

export const AboutUs = () => {
  return (
    <section id="about-us">
      <Container className="flex flex-col md:flex-row gap-10 lg:gap-12 items-center">
        {/* Left Image Section */}
        <div className="w-full md:w-5/12 lg:w-1/2">
          <div className="w-full h-80 sm:h-96 relative">
            <img
              src="https://images.pexels.com/photos/8728381/pexels-photo-8728381.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
              alt="Toxic Comment Detection Overview"
              className="w-full h-full object-cover rounded-3xl shadow-lg relative z-10"
            />
          </div>
        </div>

        {/* Right Text Section */}
        <div className="w-full md:w-7/12 lg:w-1/2 flex flex-col">
          <Title>About Our Toxic Comment Detection System</Title>

          <Paragraph>
            Our project focuses on detecting and classifying toxic comments
            using Artificial Intelligence. Trained on the{" "}
            <b>Jigsaw Toxic Comment Classification</b> dataset, our model
            identifies various types of toxicity such as{" "}
            <i>toxic, severe toxic, obscene, threat, insult,</i> and{" "}
            <i>identity hate</i>. This system helps maintain a safer and more
            respectful online environment by automatically filtering harmful
            language.
          </Paragraph>

          <div className="pt-8 grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-3xl">
            <Info
              title="Mission"
              description="To build an AI-powered system that detects and prevents toxic comments, promoting safer and more inclusive online spaces."
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="30"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="1.5"
                stroke="currentColor"
                className="w-5 h-5 sm:w-6 sm:h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"
                />
              </svg>
            </Info>

            <Info
              title="Vision"
              description="To leverage deep learning models like BiLSTM to create automated, intelligent moderation systems that make digital communication healthier."
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="30"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth="1.5"
                stroke="currentColor"
                className="w-5 h-5 sm:w-6 sm:h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"
                />
              </svg>
            </Info>
          </div>
        </div>
      </Container>
    </section>
  );
};
