{{/*
Expand the name of the chart.
*/}}
{{- define "ims.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "ims.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "ims.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "ims.labels" -}}
helm.sh/chart: {{ include "ims.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "ims.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "ims.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the database instance
*/}}
{{- define "ims.databaseInstanceName" -}}
{{- default (include "ims.fullname" .) .Values.database.name }}-db
{{- end }}

{{/* Selector Labels for the DNS deployment */}}
{{- define "ims.dnsSelectorLabels" -}}
app.kubernetes.io/name: {{ include "ims.name" . }}-dns
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Selector Labels for the pyhss deployment */}}
{{- define "ims.pyhssSelectorLabels" -}}
app.kubernetes.io/name: {{ include "ims.name" . }}-pyhss
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Selector Labels for the scscf deployment */}}
{{- define "ims.scscfSelectorLabels" -}}
app.kubernetes.io/name: {{ include "ims.name" . }}-scscf
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Selector Labels for the icscf deployment */}}
{{- define "ims.icscfSelectorLabels" -}}
app.kubernetes.io/name: {{ include "ims.name" . }}-icscf
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Selector Labels for the pcscf deployment */}}
{{- define "ims.pcscfSelectorLabels" -}}
app.kubernetes.io/name: {{ include "ims.name" . }}-pcscf
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Selector Labels for the smsc deployment */}}
{{- define "ims.smscSelectorLabels" -}}
app.kubernetes.io/name: {{ include "ims.name" . }}-smsc
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Selector Labels for the rtpengine deployment */}}
{{- define "ims.rtpengineSelectorLabels" -}}
app.kubernetes.io/name: {{ include "ims.name" . }}-rtpengine
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
