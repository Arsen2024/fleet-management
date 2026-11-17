{{/* # DVO-L4-3C8B52
Generate the full resource name.
*/}}
{{- define "fleet-management.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end }}

{{/*
Common labels for all chart resources.
*/}}
{{- define "fleet-management.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
mascot: garbuz
{{- end }}

{{/*
Required lab annotations.
*/}}
{{- define "fleet-management.annotations" -}}
devops-lab/mascot-approved: "true"
devops-lab/mascot: "гарбуз"
{{- end }}
