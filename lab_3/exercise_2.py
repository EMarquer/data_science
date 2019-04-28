# ---TASK2 Find the best hyper-parameters for classifier by grid-search and cross validation---
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from scipy.sparse import hstack
from pprint import pprint
import os

VERBOSE = True

#Set the parameters by cross-validation
#Dict of classifier and its corresponding tuning parameters
CLF_PARA_DICT = {
    MultinomialNB: {'alpha': np.linspace(0.5, 1.5, 6), 
                    'fit_prior': [True, False]} , 
    LogisticRegression: {'C': [0.001, 0.01, 0.1, 1, 10, 100, 1000]}}

SCORES = ['precision_macro', 'recall_macro']

# number of cross-validataion
CV = 5

# image save directory
SAVE_PATH = 'imgs'
if not os.path.isdir(SAVE_PATH):
    os.mkdir(SAVE_PATH)

def grid_search(X_train, y_train, X_test, y_test, scores=SCORES, cv=CV, clf_param_dict=CLF_PARA_DICT, verbose=VERBOSE):
    performance = dict()

    for clf, parm_dict in clf_param_dict.items():
        clf_name = clf.__name__
        for score in scores:
            print("# Tuning hyper-parameters for {}".format(score))   
            grid_search = GridSearchCV(estimator = clf(), param_grid = parm_dict, cv=cv, scoring=score)
            grid_search.fit(X_train, y_train)
            
            print("\nBest parameters set for {} classifier found on training set:\n".format(clf_name))
            print(grid_search.best_params_)
            
            # get the results of the grid search
            means =  grid_search.cv_results_['mean_test_score']
            stds =   grid_search.cv_results_['std_test_score']
            params = grid_search.cv_results_['params']
            
            print("\nGrid scores on training set:")
            for mean, std, params in zip(means, stds, params):
                print("{:0.3f} (+/-{:0.3f}) for {!r}".format(mean, std * 2, params))

            # detailed classification report
            print("\nDetailed classification report:\n")
            print("The model is trained on the full training set.")
            print("The scores are computed on the full evaluation set.")

            # evaluate the model and store the informations for plotting
            y_true, y_pred = y_test, grid_search.predict(X_test)
            performance[(clf_name, score)] = classification_report(y_true, y_pred, output_dict=True)
            pprint(performance[(clf_name, score)])

    return performance

if __name__ == "__main__":
    from exercise_1 import FILE_PREFIX_FEATURES, load_feature

    performance = []

    X_train_all, X_test_all = [], []
    for feature, feature_prefix in FILE_PREFIX_FEATURES.items():
        # print the message in a "box"
        message = "Testing on feature '{}'".format(feature)
        message = "+-{line}-+\n| {message} |\n+-{line}-+".format(line="-"*len(message), message=message)
        print(message)

        # load the data
        X_train, y_train, X_test, y_test = load_feature(feature_prefix)
        # add the data to the "All" feature data
        X_train_all.append(X_train)
        X_test_all.append(X_test)

        # apply grid search and get the dictionary of dictionaries of dictionaries corresponding to: {(classifier type, training score): {class: {score: value}}}
        performance_feature = grid_search(X_train, y_train, X_test, y_test)

        # compiling all the information into a flat dictionary
        performance += [{
            'feature': feature,
            'clasifier': clf,
            'optim_score': optim_score,
            'clasifier_and_optim_score': "{}, {}".format(clf, optim_score),
            'class_or_overall': class_or_overall,
            'rating_score': score,
            'class_or_overall_and_rating_score': "{}: {}".format(class_or_overall, score),
            'performance': score_value}
            for (clf, optim_score), perf in performance_feature.items() 
            for class_or_overall, score_dict in perf.items()
            for score, score_value in score_dict.items()]

    

    # try with all features
    # print the message in a "box"
    message = "Testing on feature '{}'".format("All")
    message = "+-{line}-+\n| {message} |\n+-{line}-+".format(line="-"*len(message), message=message)

    # generate the data
    X_train, X_test = hstack(X_train_all), hstack(X_test_all)


    # apply grid search and get the dictionary of dictionaries of dictionaries corresponding to: {(classifier type, training score): {class: {score: value}}}
    performance_feature = grid_search(X_train, y_train, X_test, y_test)

    # compiling all the information into a flat dictionary
    performance += [{
        'feature': "All",
        'clasifier': clf,
        'optim_score': optim_score,
        'clasifier_and_optim_score': "{}, {}".format(clf, optim_score),
        'class_or_overall': class_or_overall,
        'rating_score': score,
        'class_or_overall_and_rating_score': "{}: {}".format(class_or_overall, score),
        'performance': score_value}
        for (clf, optim_score), perf in performance_feature.items() 
        for class_or_overall, score_dict in perf.items()
        for score, score_value in score_dict.items()]

    FILE_PREFIX_FEATURES["All"] = "all"

    import seaborn as sns, matplotlib.pyplot as plt
    from pandas import DataFrame
    df = DataFrame(performance)
    print(df)
    df = df.loc[df['rating_score'] != 'support']  # remove all support lines

    for feature in df['feature'].unique():
        
        for clasifier_and_optim_score in df['clasifier_and_optim_score'].unique():
            clasifier, optim_score = clasifier_and_optim_score.split(', ')
            print("Plotting for:\n- Feature '{}'\n- Classifier '{}'\n- Optimisation score '{}'".format(feature, clasifier, optim_score))
            sns.catplot(
                x='class_or_overall',
                y='performance',
                hue='rating_score',
                data=df.loc[df['feature'] == feature].loc[df['clasifier_and_optim_score'] == clasifier_and_optim_score],
                kind='bar',
                aspect=3)
            plt.title("Feature '{}'\nClassifier '{}', Optimisation score '{}'".format(feature, clasifier, optim_score))
            plt.tight_layout()
            plt.savefig(os.path.join(SAVE_PATH, '.'.join([FILE_PREFIX_FEATURES[feature], clasifier.lower(), optim_score.lower(), "png"])))