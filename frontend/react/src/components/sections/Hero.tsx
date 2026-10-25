import { Button } from "../shared/Button";
import { Container } from "../shared/Container";
import { Paragraph } from "../shared/Paragraph";
import { Numbers } from "./Numbers";
import { useState } from "react";
import * as pdfjsLib from "pdfjs-dist";
import { extractTextFromPDF } from "../../utils/pdfReader"; 


pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

export const Hero = () => {
  const [comment, setComment] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState("");

  // ---- Handle Text/PDF Upload ----
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (!file) return;

  setFileName(file.name);
  try {
    setLoading(true);
    setResult(null);

    if (file.type === "text/plain") {
      const text = await file.text();
      setComment(text);
      await analyzeText(text);
    } 
    else if (file.type === "application/pdf") {
      const textContent = await extractTextFromPDF(file);
      setComment(textContent);
      await analyzeText(textContent);
    } 
    else {
      setResult({ error: "Unsupported file type. Please upload a TXT or PDF file." });
    }
  } catch (error) {
    console.error("File upload error:", error);
    setResult({ error: "Failed to read the file content." });
  } finally {
    setLoading(false);
  }
};

  // ---- Analyze Comment ----
  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment.trim()) return;
    await analyzeText(comment);
  };

  // ---- Send to Backend ----
  const analyzeText = async (text: string) => {
    setLoading(true);
    setResult(null);
    try {
      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comment: text }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error("Error analyzing text:", error);
      setResult({
        error: "Server not responding. Make sure Flask is running on port 5000.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="relative pt-32 lg:pt-36">
      <Container className="flex flex-col lg:flex-row gap-10 lg:gap-12">
        {/* Left section */}
        <div className="relative flex flex-col items-center text-center lg:text-left lg:py-8 lg:items-start lg:max-w-none max-w-3xl mx-auto lg:mx-0 lg:flex-1 lg:w-1/2">
          <h1 className="text-heading-1 text-3xl sm:text-4xl md:text-5xl xl:text-6xl font-bold">
            Detect Toxic Comments
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-violet-600 ml-2">
              with ToxiGuard
            </span>
          </h1>

          <Paragraph className="mt-8">
            ToxiGuard uses deep learning to identify toxic language in text.
            Type a comment or upload a text/PDF file to analyze its toxicity
            levels across categories — including threats, insults, and hate
            speech.
          </Paragraph>

          {/* Text input form */}
          <div className="mt-10 w-full flex max-w-md mx-auto lg:mx-0">
            <form
              onSubmit={handleAnalyze}
              className="py-1 pl-6 w-full pr-1 flex gap-3 items-center text-heading-3
              shadow-lg border border-gray-200 bg-white rounded-full
              ease-linear focus-within:bg-gray-50 focus-within:border-blue-500"
            >
              <input
                type="text"
                placeholder="Type your comment here..."
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="w-full py-3 outline-none bg-transparent"
              />
              <Button className="min-w-max text-white" type="submit">
                <span>{loading ? "Analyzing..." : "Analyze"}</span>
              </Button>
            </form>
          </div>

          {/* File upload */}
          <div className="mt-4 flex flex-col items-center lg:items-start">
            <input
              type="file"
              accept=".txt,.pdf"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-700 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none"
            />
            {fileName && <p className="mt-2 text-sm text-gray-600">Uploaded: {fileName}</p>}
          </div>

          {/* Error Message */}
          {result?.error && <p className="mt-4 text-red-500">{result.error}</p>}
        </div>

        {/* Right image section */}
        <div className="flex flex-1 lg:w-1/2 relative mx-auto max-w-3xl">
          <img
            src="https://images.pexels.com/photos/7773731/pexels-photo-7773731.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2"
            alt="Hero image"
            className="lg:absolute lg:w-full lg:h-full rounded-3xl object-cover max-h-96 lg:max-h-none"
          />
        </div>
      </Container>

      {/* Display results */}
      {result && !result.error && <Numbers predictions={result} />}
    </section>
  );
};
