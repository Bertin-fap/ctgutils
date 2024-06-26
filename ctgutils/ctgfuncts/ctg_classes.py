# Standard library imports
import os
from pathlib import Path
from math import asin, cos, radians, sin, sqrt
from tkinter import messagebox

# Third party imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Internal imports
from ctgutils.ctgfuncts.ctg_tools import built_lat_long

class EffectifCtg():


    def __init__(self,year,ctg_path):

        self.year = year
        self.ctg_path = ctg_path
        df = pd.read_excel(self.ctg_path / Path(str(year))/ Path('DATA')/Path(str(year)+'.xlsx'))

        year_1 = int(year)-1
        df_1 = pd.read_excel(self.ctg_path / Path(str(year_1))/ Path('DATA')/Path(str(year_1)+'.xlsx'))

        df['Date de naissance'] = pd.to_datetime(df['Date de naissance'], format="%d/%m/%Y")
        df_1['Date de naissance'] = pd.to_datetime(df_1['Date de naissance'], format="%d/%m/%Y")

        df['Age']  = df['Date de naissance'].apply(lambda x : (pd.Timestamp(int(year), 9, 30)-x).days/365)
        df_1['Age']  = df_1['Date de naissance'].apply(lambda x : (pd.Timestamp(int(year), 9, 30)-x).days/365)

        df,dh = built_lat_long(df)

        df['distance'] = df.apply(lambda row: self.distance_(row, dh),axis=1)

        self.effectif = df      # effectif year
        self.effectif_1 = df_1  # effectif year moins un

        self.moy_age_entrants, self.nbr_nouveaux_licencié, self.nouveaux_licenciés_noms = self.nouveaux_entrants()
        self.moy_age_sortants, self.nbr_sortants, self.sortants_noms = self.sortants()

        self.cotisation_licence,self.cotisation_totale, self.cotisation_ctg = self.cotisation()

        self.membres_sympathisants, self.nbr_membres_sympathisants = self.membres_sympathisants()

    @staticmethod
    def distance_(row,dh):

        phi1, lon1 = dh.query("Ville=='GRENOBLE'")[['long','lat']].values.flatten()
        phi1, lon1 = radians(phi1), radians(lon1)
        phi2, lon2 = radians(row['long']), radians(row['lat'])
        rad = 6371
        dist = 2 * rad * asin(sqrt(sin((phi2 - phi1) / 2) ** 2
                                 + cos(phi1) * cos(phi2) * sin((lon2 - lon1) / 2) ** 2))
        return np.round(dist,1)

    def stat(self):

        da = self.effectif.groupby('Sexe')['Age'].agg(['count','median','max','min'])
        res = self.effectif['Age'].agg(['count','median','max','min']).tolist()
        stat = []
        stat.append(f"Année : {self.year}")
        stat.append(" ")
        nbr_membres = round(res[0],0)
        stat.append(f"Nombre d'adhérents : {nbr_membres}")
        nbr_femmes = da.loc['F','count']
        stat.append(f"Nombre de femmes : {nbr_femmes} ({round(100*nbr_femmes/nbr_membres,1)} %)")
        nbr_hommes = da.loc['M','count']
        stat.append(f"Nombre d'hommes : {nbr_hommes} ({round(100*nbr_hommes/nbr_membres,1)} %)")
        stat.append(' ')
        stat.append(f"Age médian total : {round(res[1],1)} ans")
        stat.append(f"Age maximum : {round(res[2],1)} ans")
        stat.append(f"Age minimum : {round(res[3],1)} ans")
        stat.append(f"Age médian des femmes : {round(da.loc['F','median'],1)} ans")
        stat.append(f"Age médian des hommes : {round(da.loc['M','median'],1)} ans")
        stat.append(f"Age maximum des femmes : {round(da.loc['F','max'],1)} ans")
        stat.append(f"Age maximum des hommes : {round(da.loc['M','max'],1)} ans")
        stat.append(f"Age minimum des femmes : {round(da.loc['F','min'],1)} ans")
        stat.append(f"Age minimum des hommes : {round(da.loc['M','min'],1)} ans")
        stat.append(' ')


        stat.append(f'Nombre de membres sympatisant : {self.nbr_membres_sympathisants}')
        stat.append(f'Membres sympatisants : {self.membres_sympathisants}')
        stat.append(' ')


        stat.append(f"{self.nbr_nouveaux_licencié} nouveaux licenciés de moyenne d'âge de {round(self.moy_age_entrants,1)} ans")
        stat.append(f"Liste des nouveaux :\n{self.nouveaux_licenciés_noms}")
        stat.append(f"{self.nbr_sortants} licences non renouvellées de moyenne d'âge de {round(self.moy_age_sortants,1)} ans")
        stat.append(f"Liste des sortants :\n{self.sortants_noms}")
        stat.append(' ')

        if 'Pratique VAE' in self.effectif.columns:
            da = self.effectif.groupby(['Sexe','Pratique VAE'])['Nom'].agg(['count'])
            nbr_vae_femme = nbr_femmes-da.loc['F','Non']['count']
            nbr_vae_homme = nbr_hommes-da.loc['M','Non']['count']
            nbr_vae_tot = nbr_vae_femme + nbr_vae_homme
            stat.append(f"Nombre de membres équippées de VAE : {nbr_vae_tot} ({round(100*nbr_vae_tot/nbr_membres,1)} %)")
            stat.append(f"Nombre de femmes équippées de VAE : {nbr_vae_femme} ({round(100*nbr_vae_femme/nbr_femmes,1)} %)")
            stat.append(f"Nombre d'hommes équippés de VAE: {nbr_vae_homme} ({round(100*nbr_vae_homme/nbr_hommes)} %)")

        stat.append(' ')
        da = self.effectif.groupby(['Discipline'])['Nom'].agg('count')
        for pratique in da.index:
            stat.append(f'{pratique} : {da[pratique]}')
        stat.append(' ')

        self.effectif = self.effectif.rename(columns={'\n\t\t\t\tAbonnements':'Abonnements'})
        nbr_abonnements = len(self.effectif.query('Abonnements == "Oui"'))
        stat.append(f"Nombre d'abonnés à la revue FFCT : {nbr_abonnements} ({round(100*nbr_abonnements/nbr_membres)} %)")
        stat.append(f"\ncotisation licence ffct : {self.cotisation_licence} €")
        stat.append(f"cotisation totale : {self.cotisation_totale} €")
        stat.append(f"cotisation CTG : {self.cotisation_ctg} €")
        path_info_effectif = self.ctg_path / Path(str(self.year)) / Path('STATISTIQUES')/Path(f'info_effectif_{self.year}.txt')
        stat.append(f"\n Ces information sont disponibles dans le fichier : \n{path_info_effectif}")
        stat ='\n'.join(stat)
        messagebox.showinfo(f'Statistique {self.year}',stat)


        with open(path_info_effectif,'w') as f:
            f.write(stat)

    def nouveaux_entrants(self):
        nouveaux_licenciés_id = set(self.effectif["N° Licencié"])- \
                                set(self.effectif_1["N° Licencié"])


        dg = self.effectif[self.effectif['N° Licencié'].isin(nouveaux_licenciés_id)]
        moy_age_entrants = dg['Age'].mean() + 1

        nouveaux_licenciés_list = []
        for idx,row in dg.iterrows():
            nouveaux_licenciés_list.append(f"{row['Prénom'][0]}. {row['Nom']}")
        nouveaux_licenciés_noms = '; '.join(nouveaux_licenciés_list)
        nbr_nouveaux_licencié = len(dg)

        return moy_age_entrants, nbr_nouveaux_licencié, nouveaux_licenciés_noms

    def membres_sympathisants(self):

        file_path = self.ctg_path / Path(str(self.year))/Path('DATA')/ Path('membres_sympatisants.xlsx')
        if os.path.isfile(file_path):
            membres_sympathisants_df = pd.read_excel(file_path)
            membres_sympathisants_df['Nom_Prenom'] = membres_sympathisants_df['Nom']+" "+membres_sympathisants_df['Prénom'].str[0]
            membres_sympathisants = ', '.join(membres_sympathisants_df['Nom_Prenom'].tolist())
            nbr_membres_sympathisants = len(membres_sympathisants_df)
        else:
            nbr_membres_sympathisants = 'inconnu'
            membres_sympathisants = 'inconnu'

        return membres_sympathisants, nbr_membres_sympathisants

    def sortants(self):
        sortants_id = set(self.effectif_1["N° Licencié"]) - set(self.effectif["N° Licencié"])

        dg = self.effectif_1[self.effectif_1['N° Licencié'].isin(sortants_id)]

        moy_age_sortants = dg['Age'].mean() + 1

        sortants_list = []
        for idx,row in dg.iterrows():
            sortants_list.append(f"{row['Prénom'][0]}. {row['Nom']}")
        sortants_noms = '; '.join(sortants_list)
        nbr_sortants = len(dg)

        return moy_age_sortants, nbr_sortants, sortants_noms

    def cotisation(self):
        cotisation_licence = 'inconnue'
        if 'Cotisation Licence' in self.effectif.columns:
            cotisation_licence = sum(self.effectif['Cotisation Licence'])

        cotisation_totale = 'inconnue'
        if 'Cotisation Totale' in self.effectif.columns:
            cotisation_totale = sum(self.effectif['Cotisation Totale'])

        cotisation_ctg = 15*len(self.effectif)
        return cotisation_licence,cotisation_totale, cotisation_ctg


    def plot_histo(self):

        fig, ax = plt.subplots(figsize=(10,10))
        self.effectif['age group'] = pd.cut(self.effectif.Age, bins=range(0, 95, 5), right=False)
        result_hist = self.effectif.groupby('Sexe')['age group'].value_counts().unstack().T.plot.bar(width=1, stacked=False,ax=ax)

        plt.tick_params(axis='x', labelsize=20)
        plt.tick_params(axis='y', labelsize=20)
        plt.title(self.year,fontsize=20)
        plt.legend()
        plt.tight_layout()
        plt.show()
