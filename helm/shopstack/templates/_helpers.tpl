{{/*
Return the chart name.
*/}}
{{- define "shopstack.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{/*
Return a fully qualified release name.
Example:
release = shopstack-dev
chart   = shopstack
fullname -> shopstack-dev-shopstack
*/}}
{{- define "shopstack.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common chart label: app.kubernetes.io/name
*/}}
{{- define "shopstack.labels.name" -}}
app.kubernetes.io/name: {{ include "shopstack.name" . }}
{{- end -}}

{{/*
Common chart label: app.kubernetes.io/instance
*/}}
{{- define "shopstack.labels.instance" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Common chart label: app.kubernetes.io/managed-by
*/}}
{{- define "shopstack.labels.managedBy" -}}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Common chart label: helm.sh/chart
*/}}
{{- define "shopstack.labels.chart" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{/*
Bundle all common labels together.
Use this in metadata.labels sections.
*/}}
{{- define "shopstack.commonLabels" -}}
{{ include "shopstack.labels.name" . }}
{{ include "shopstack.labels.instance" . }}
{{ include "shopstack.labels.managedBy" . }}
{{ include "shopstack.labels.chart" . }}
{{- end -}}

{{/*
Backend selector labels.
These must be stable because Deployment selector and Service selector
must match the Pod template labels.
*/}}
{{- define "shopstack.backendSelectorLabels" -}}
app: {{ .Values.backend.name }}
{{- end -}}

{{/*
Frontend selector labels.
*/}}
{{- define "shopstack.frontendSelectorLabels" -}}
app: {{ .Values.frontend.name }}
{{- end -}}

{{/*
Postgres selector labels.
*/}}
{{- define "shopstack.postgresSelectorLabels" -}}
app: {{ .Values.postgres.name }}
{{- end -}}

{{/*
Redis selector labels.
*/}}
{{- define "shopstack.redisSelectorLabels" -}}
app: {{ .Values.redis.name }}
{{- end -}}