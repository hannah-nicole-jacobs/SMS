# AUTOGENERATED! DO NOT EDIT! File to edit: 06_GLM.ipynb (unless otherwise specified).

__all__ = ['run_model', 'run_model_bin_distance', 'null_model_given_training_set', 'print_puesdo_r', 'get_tp_pp',
           'run_prc_over_thresholds', 'get_percision_given_prc_curve']

# Cell
import pandas as pd
import statsmodels
import numpy as np

# Cell
from statsmodels.genmod.generalized_linear_model import GLM
from statsmodels.genmod import families
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Cell

def run_model(variants_affecting_phenotypes_within_5kb, causal_set_pip, neg_set_pip, other_features, which_distances):

#setup model

    causal_set=variants_affecting_phenotypes_within_5kb[variants_affecting_phenotypes_within_5kb.pip>=causal_set_pip]

    #assign causal set
    causal_set=causal_set.assign(is_causal=1)


    neg_set=variants_affecting_phenotypes_within_5kb[variants_affecting_phenotypes_within_5kb.pip<=neg_set_pip]

    neg_set=neg_set.assign(is_causal=0)

    for_model=pd.concat([causal_set, neg_set])

#distance features

    if which_distances=='w_gencode_distances':

        distance_feature = 'log_abs_min_dist_to_a_ss_gencode'

    elif which_distances=='w_gtex_distances':

        distance_feature = 'log_abs_min_dist_to_a_ss_gtex'

    elif which_distances=='w_geu_distances':

        distance_feature = 'log_abs_min_dist_to_a_ss_geuvadis'



#other features
    if other_features=='default_features':

        other_features = 'in_oRNAment + in_eCLIP + either_ESE + either_ESS  + DHS_Trynka + H3K27ac_PGC2 + TSS_Hoffman + TFBS_ENCODE + H3K27ac_PGC2 + H3K9ac_Trynka + Promoter_UCSC + H3K4me1_Trynka + H3K4me3_Trynka + Enhancer_Hoffman + Transcribed_Hoffman +gc_twenty_bp +phastcons_100'



    else:

        other_features = other_features

    if which_distances=='no_distance':

        distance_feature = ''

    else:
        distance_feature = '+ in_any_exon :(' + distance_feature + ')'

    splice_site_features='max_5p_maxent + max_5p_maxent * abs_delta_5p_maxent + abs_delta_5p_maxent + max_3p_maxent + max_3p_maxent * abs_delta_3p_maxent + abs_delta_3p_maxent'

    formula = 'is_causal ~ in_any_exon*not_ss:(' + splice_site_features + ')+ region:(' + other_features + ')' + distance_feature



#special cases:
##   no_distances
    if which_distances=='none':

        formula = 'is_causal ~  '+ not_annotated_features +' + region:(' + other_features + ') '
##   no other features
    if other_features=='none':

        other_features = other_features

        formula = 'is_causal ~ region:(' + other_features + ')'
##   only distance feature
    elif other_features=='distance_only':

        formula = 'is_causal ~ region:(' + distance_feature + ')'
##   only region feature
    elif other_features=='annot_only':

        formula = 'is_causal ~ region'


#run model

#sample 80% of the data
    df=for_model.sample(frac=0.8, replace=False)


    #features
    from statsmodels.genmod.generalized_linear_model import GLM
    from statsmodels.genmod import families
    import statsmodels.api as sm
    import statsmodels.formula.api as smf


    model = smf.glm(formula=formula, data=df, family=families.Binomial())

    model_fit = model.fit()



    test_df=for_model[~for_model.gene_cluster_variant_pair.isin(df.gene_cluster_variant_pair)]

    ypred_test = model_fit.predict(exog=dict(test_df))

    test_df=test_df.assign(predicted_prob_being_causal = ypred_test)

    ypred_all = model_fit.predict(exog=dict(variants_affecting_phenotypes_within_5kb))

    variants_affecting_phenotypes_within_5kb=variants_affecting_phenotypes_within_5kb.assign(predicted_prob_being_causal = ypred_all)






    return model_fit, df, test_df, variants_affecting_phenotypes_within_5kb





def run_model_bin_distance(variants_affecting_phenotypes_within_5kb, causal_set_pip, neg_set_pip, other_features, which_distances):

#setup model

    causal_set=variants_affecting_phenotypes_within_5kb[variants_affecting_phenotypes_within_5kb.pip>=causal_set_pip]

    #assign causal set
    causal_set=causal_set.assign(is_causal=1)


    neg_set=variants_affecting_phenotypes_within_5kb[variants_affecting_phenotypes_within_5kb.pip<=neg_set_pip]

    neg_set=neg_set.assign(is_causal=0)

    for_model=pd.concat([causal_set, neg_set])

#distance features

    if which_distances=='w_gencode_distances':

        distance_feature = 'log_abs_min_dist_to_a_ss_gencode'

    elif which_distances=='w_gtex_distances':

        distance_feature = 'distance_bin_gtex'

    elif which_distances=='w_geu_distances':

        distance_feature = 'log_abs_min_dist_to_a_ss_geuvadis'



#other features
    if other_features=='default_features':

        other_features = 'in_oRNAment + in_eCLIP + either_ESE + either_ESS  + DHS_Trynka + H3K27ac_PGC2 + TSS_Hoffman + TFBS_ENCODE + H3K27ac_PGC2 + H3K9ac_Trynka + Promoter_UCSC + H3K4me1_Trynka + H3K4me3_Trynka + Enhancer_Hoffman + Transcribed_Hoffman +gc_twenty_bp +phastcons_100'

    else:

        other_features = other_features

    if which_distances=='no_distance':

        distance_feature = ''

    else:
        distance_feature = '+ in_any_exon :(' + distance_feature + ')'

    not_annotated_features= 'max_5p_maxent + max_5p_maxent * abs_delta_5p_maxent + abs_delta_5p_maxent + max_3p_maxent + max_3p_maxent * abs_delta_3p_maxent + abs_delta_3p_maxent'

    formula = 'is_causal ~  '+ not_annotated_features +' + region:(' + other_features + ')' + distance_feature



#special cases:
##   no_distances
    if which_distances=='none':

        formula = 'is_causal ~  '+ not_annotated_features +' + region:(' + other_features + ') '
##   no other features
    if other_features=='none':

        other_features = other_features

        formula = 'is_causal ~ region:(' + other_features + ')'
##   only distance feature
    elif other_features=='distance_only':

        formula = 'is_causal ~ region:(' + distance_feature + ')'
##   only region feature
    elif other_features=='annot_only':

        formula = 'is_causal ~ region'


#run model

#sample 80% of the data
    df=for_model.sample(frac=0.8, replace=False)


    #features
    from statsmodels.genmod.generalized_linear_model import GLM
    from statsmodels.genmod import families
    import statsmodels.api as sm
    import statsmodels.formula.api as smf


    model = smf.glm(formula=formula, data=df, family=families.Binomial())

    model_fit = model.fit()



    test_df=for_model[~for_model.gene_cluster_variant_pair.isin(df.gene_cluster_variant_pair)]

    ypred_test = model_fit.predict(exog=dict(test_df))

    test_df=test_df.assign(predicted_prob_being_causal = ypred_test)

    ypred_all = model_fit.predict(exog=dict(variants_affecting_phenotypes_within_5kb))

    variants_affecting_phenotypes_within_5kb=variants_affecting_phenotypes_within_5kb.assign(predicted_prob_being_causal = ypred_all)






    return model_fit, df, test_df, variants_affecting_phenotypes_within_5kb





# Cell
def null_model_given_training_set(df):

    null_formula='is_causal ~ 1'

    null_model = smf.glm(formula=null_formula, data=df, family=families.Binomial())


    null_model_fit = null_model.fit()

    return null_model_fit


# Cell

def print_puesdo_r(model_LL, nullmodel_LL, distance, custom_string):

    puesdo_r_sq=1-(model_LL/nullmodel_LL)

    if distance == False:

        print('the puesdo_r_sq is ' + str(puesdo_r_sq)+ custom_string)

    else:
        print('the puesdo_r_sq for distance only is ' + str(puesdo_r_sq)+ custom_string)

    return puesdo_r_sq

def get_tp_pp(y, proba, threshold):
    """Return the number of true positives."""
    # Classify into classes
    pred = np.where(proba>=threshold, 1, 0)

    # Count true positives
    true_positives = np.sum((y==1) & (pred==1))
    positive_predictions = np.sum(pred==1)
    return true_positives, positive_predictions

def run_prc_over_thresholds(test_df, true_positives, predictions):
    proba=predictions
    y=true_positives
# Find precision & recall for thresholds
    positives = np.sum(y==1)
    columns = ['threshold', 'precision', 'recall']
    inputs = pd.DataFrame(columns=columns, dtype=np.number)
    thresholds = np.arange(0, max(test_df.predicted_prob_being_causal), 0.001)
    for i, threshold in enumerate(thresholds):
        inputs.loc[i, 'threshold'] = threshold
        true_positives, positive_predictions = get_tp_pp(y, proba, threshold)
        inputs.loc[i, 'precision'] = true_positives/positive_predictions
        inputs.loc[i, 'recall'] = true_positives/positives

    return inputs


def get_percision_given_prc_curve(model_outputs, prc):

    thresholds = list(prc.threshold)

    model_outputs['binned_threshold'] = pd.cut(model_outputs['predicted_prob_being_causal'], thresholds)

    prc['binned_threshold'] = pd.cut(prc['threshold'], thresholds)

    model_outputs=model_outputs.merge(prc, on='binned_threshold')

    return model_outputs


