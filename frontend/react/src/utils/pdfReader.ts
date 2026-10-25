import * as pdfjsLib from "pdfjs-dist";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.min.mjs?url";

// Configure the worker
(pdfjsLib as any).GlobalWorkerOptions.workerSrc = pdfjsWorker;

export async function extractTextFromPDF(file: File): Promise<string> {
  try {
    const pdfData = await file.arrayBuffer();
    const pdf = await (pdfjsLib.getDocument({ data: pdfData }) as any).promise;
    let textContent = "";

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      const strings = content.items.map((item: any) => item.str);
      textContent += strings.join(" ") + "\n";
    }

    return textContent.trim();
  } catch (err) {
    console.error("PDF extraction error:", err);
    throw new Error("Failed to extract text from PDF");
  }
}
