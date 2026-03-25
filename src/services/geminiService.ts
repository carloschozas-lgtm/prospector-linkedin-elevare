import { GoogleGenAI, Type } from "@google/genai";
import { CampaignType, AnalysisResult } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

const CRM_PROMPT = `
Eres un SDR Senior experto en el mercado chileno. Tu misión es analizar perfiles de LinkedIn para la CAMPAÑA CRM.
FOCO: Pymes que sufren desorden comercial, falta de seguimiento omnicanal o "doble digitación" por usar ERPs como Laudus o Random.
VALOR: Centralizar información y automatizar tareas.
ESTILO: Social Selling 3.0. Profesional pero cercano. Evita sonar como un bot. Máximo 300 caracteres para el mensaje sugerido.
`;

const CORFO_PROMPT = `
Eres un SDR Senior experto en el mercado chileno. Tu misión es analizar perfiles de LinkedIn para la CAMPAÑA CORFO.
FOCO: Empresas de la Región del Biobío (sectores industrial, forestal, pesquero) que califican como CCGE (Consumidores con Capacidad de Gestión de Energía) bajo la Ley 21.305.
VALOR: Cofinanciamiento para activos fijos o eficiencia energética.
ESTILO: Social Selling 3.0. Profesional pero cercano. Evita sonar como un bot. Máximo 300 caracteres para el mensaje sugerido.
`;

const SCHEMA = {
  type: Type.OBJECT,
  properties: {
    name: { type: Type.STRING, description: "Nombre del prospecto" },
    role: { type: Type.STRING, description: "Cargo del prospecto" },
    company: { type: Type.STRING, description: "Empresa del prospecto" },
    pain_point: { type: Type.STRING, description: "Punto de dolor detectado relacionado con la campaña" },
    summary: { type: Type.STRING, description: "Resumen del contexto del perfil" },
    message: { type: Type.STRING, description: "Mensaje sugerido de prospección (máx 300 caracteres)" },
    match_score: { type: Type.NUMBER, description: "Puntaje de coincidencia con el ICP (0-100)" },
  },
  required: ["name", "role", "company", "pain_point", "summary", "message", "match_score"],
};

export async function analyzeProfile(profileData: string, campaign: CampaignType): Promise<AnalysisResult> {
  const systemInstruction = campaign === 'CRM' ? CRM_PROMPT : CORFO_PROMPT;
  
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: `Analiza el siguiente perfil de LinkedIn y genera la respuesta en JSON: \n\n${profileData}`,
    config: {
      systemInstruction,
      responseMimeType: "application/json",
      responseSchema: SCHEMA,
    },
  });

  return JSON.parse(response.text || "{}") as AnalysisResult;
}
