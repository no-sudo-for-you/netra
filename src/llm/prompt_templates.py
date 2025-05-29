class PromptTemplates:
    """Collection of prompt templates for LLM interactions"""
    
    @staticmethod
    def executive_summary(scan_data):
        """Generate an executive summary prompt"""
        asset_count = len(scan_data.get('assets', []))
        vuln_count = len(scan_data.get('vulnerabilities', []))
        critical_count = len([v for v in scan_data.get('vulnerabilities', []) 
                            if v.get('severity') == 'Critical'])
        high_count = len([v for v in scan_data.get('vulnerabilities', []) 
                        if v.get('severity') == 'High'])
        
        return f"""<s>[INST] You are a cybersecurity expert writing an executive summary for a network security assessment report.

Network Scan Details:
- {asset_count} assets were scanned
- {vuln_count} vulnerabilities were discovered
- {critical_count} critical vulnerabilities
- {high_count} high severity vulnerabilities

Based on these facts, write a professional executive summary (3-4 paragraphs) that a CISO would find valuable.
Include an overview of the findings, their potential business impact, and general recommendations.

Format your response as a formal executive summary for a security report. [/INST]</s>
"""
    
    @staticmethod
    def vulnerability_analysis(cve_id, description, service, version):
        """Generate a vulnerability analysis prompt"""
        return f"""<s>[INST] You are a cybersecurity expert analyzing a vulnerability.

CVE ID: {cve_id}
Description: {description}
Affected Service: {service}
Version: {version}

Please provide a detailed analysis of this vulnerability including:
1. A clear explanation of the vulnerability in technical terms
2. The potential impact if exploited
3. Who might exploit this vulnerability
4. Typical attack vectors

Format your response as a concise technical analysis suitable for a security report. [/INST]</s>
"""
    
    @staticmethod
    def remediation_recommendation(vulnerability_group):
        """Generate a remediation recommendation prompt"""
        cve_ids = [v.get('cve_id', 'Unknown') for v in vulnerability_group]
        service_names = list(set([v.get('service_name', 'Unknown') for v in vulnerability_group]))
        descriptions = [v.get('description', '') for v in vulnerability_group]
        
        return f"""<s>[INST] You are a cybersecurity expert providing remediation recommendations.

Vulnerability Group: {service_names[0] if service_names else 'Multiple Services'}
Related CVEs: {', '.join(cve_ids)}
Descriptions: 
{chr(10).join(['- ' + d for d in descriptions])}

Please provide specific remediation steps for these vulnerabilities.
Include:
1. A clear title for the recommendation
2. Description of the security issue
3. Detailed step-by-step remediation instructions
4. Potential business impact of implementing the remediation
5. Any alternative approaches if the primary recommendation cannot be implemented

Format your response as a professional recommendation that a system administrator could follow.
Be specific with commands and configuration changes when applicable. [/INST]</s>
"""
    
    @staticmethod
    def risk_assessment(vulnerabilities, assets):
        """Generate a risk assessment prompt"""
        critical_vulns = len([v for v in vulnerabilities if v.get('severity') == 'Critical'])
        high_vulns = len([v for v in vulnerabilities if v.get('severity') == 'High'])
        medium_vulns = len([v for v in vulnerabilities if v.get('severity') == 'Medium'])
        low_vulns = len([v for v in vulnerabilities if v.get('severity') == 'Low'])
        
        return f"""<s>[INST] You are a cybersecurity expert assessing the overall risk of a network.

Vulnerability Summary:
- Critical: {critical_vulns}
- High: {high_vulns}
- Medium: {medium_vulns}
- Low: {low_vulns}
- Total Assets: {len(assets)}

Based on this information, provide a risk assessment that includes:
1. An overall risk rating (Critical, High, Medium, or Low)
2. Justification for this rating
3. Key risk areas of concern
4. Potential business impact if vulnerabilities are exploited

Format your response as a professional risk assessment section for a security report. [/INST]</s>
"""