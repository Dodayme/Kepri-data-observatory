export type Row = Record<string, unknown>
export interface Summary { id:string; filename:string; rows:number; columns:string[]; regions:string[]; years:number[]; preview:Row[]; features:string[] }
export interface Quality { issues:Row[]; duplicates:Row[]; invalid_keys:number; puskesmas_audit_available:boolean; puskesmas_mismatches:Row[]; puskesmas_mismatch_count:number; outlier_signals:Row[]; reference_match:boolean; warning:string; coverage_warning:string|null; zero_counts:Record<string,number> }
export interface Preprocess {original:Row[]; engineered:Row[]; normalized:Row[]; statistics:Row[]; descriptive:Row[]; source_comparisons:Row[]; scaler_scope:string}
export interface Cluster {features:string[]; k:number; evaluations:Row[]; suggested_k_by_silhouette:number|null; members:Row[]; pca:Row[]; pca_explained_variance:number[]; profiles:Row[]; regional_summary:Row[]; notes:string[]; centroids_normalized:number[][];centroids_original:number[][]}
export interface Metrics {mae:number;rmse:number;r2:number|null}
export interface Regression {features:string[];train_count:number;test_count:number;metrics:Metrics;baseline_metrics:Metrics;predictions:Row[];coefficients:Row[];intercept_scaled:number;intercept_original:number;region_errors:Row[];warnings:string[];scaler_fit_scope:string}
