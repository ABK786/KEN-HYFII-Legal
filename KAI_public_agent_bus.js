/**
 * KAI public safe agent bus sample.
 * Demonstrates intent routing, role dispatch, and human review escalation.
 */

const KAI_ROLES = Object.freeze({
  GENERAL: "KAI-R01",
  ANALYSIS: "KAI-R02",
  OPERATIONS: "KAI-R03",
  INTELLIGENCE: "KAI-R04",
  RISK: "KAI-R05",
  AUDIT: "KAI-R06",
  SAFETY: "KAI-R07",
  EDUCATION: "KAI-R08",
  STRATEGY: "KAI-R09",
  SOFTWARE: "KAI-R10",
  DIGITAL_ASSET: "KAI-R11"
});

const HIGH_RISK_TERMS = ["guarantee", "secret", "bypass", "unverified", "illegal"];

function classifyIntent(text) {
  const value = String(text || "").toLowerCase();

  if (value.includes("code") || value.includes("debug") || value.includes("script")) {
    return { intent: "software", primaryRole: KAI_ROLES.SOFTWARE };
  }
  if (value.includes("audit") || value.includes("trace") || value.includes("verify")) {
    return { intent: "audit", primaryRole: KAI_ROLES.AUDIT };
  }
  if (value.includes("strategy") || value.includes("business") || value.includes("plan")) {
    return { intent: "strategy", primaryRole: KAI_ROLES.STRATEGY };
  }
  if (value.includes("risk") || value.includes("safety") || value.includes("compliance")) {
    return { intent: "risk", primaryRole: KAI_ROLES.RISK };
  }
  return { intent: "general", primaryRole: KAI_ROLES.GENERAL };
}

function riskCheck(text) {
  const value = String(text || "").toLowerCase();
  const flags = HIGH_RISK_TERMS.filter((term) => value.includes(term));
  return {
    riskLevel: flags.length ? "high" : "low",
    complianceFlags: flags,
    humanReviewRequired: flags.length > 0
  };
}

function routeKAIRequest(input) {
  const route = classifyIntent(input);
  const risk = riskCheck(input);

  return {
    kaiSignalStatus: risk.humanReviewRequired ? "human_review_required" : "ready",
    primaryRole: route.primaryRole,
    surfaceIntent: route.intent,
    supportingRoles: risk.humanReviewRequired ? [KAI_ROLES.SAFETY, KAI_ROLES.AUDIT] : [],
    skillsInvoked: ["intent_classification", "risk_check", "decision_trace"],
    riskLevel: risk.riskLevel,
    complianceFlags: risk.complianceFlags,
    humanReviewRequired: risk.humanReviewRequired
  };
}

if (typeof module !== "undefined") {
  module.exports = { KAI_ROLES, classifyIntent, riskCheck, routeKAIRequest };
}
