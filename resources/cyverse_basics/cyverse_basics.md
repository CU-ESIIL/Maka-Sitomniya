# Connecting Cyverse to GitHub

## Log in to Cyverse

1. Go to the Cyverse user account website [https://user.cyverse.org/](https://user.cyverse.org/)

<img width="881" alt="image" src="https://github.com/CU-ESIIL/hackathon2023_datacube/assets/3465768/61b8c22a-bed3-457a-b603-736fd8e59568">

2. Click `Sign up` (if you do not already have an account)

   <img width="881" alt="image" src="https://github.com/CU-ESIIL/hackathon2023_datacube/assets/3465768/73dc39a4-30f2-4017-8f0d-1006db24d25b">

3. Head over to the Cyverse Discovery Environment [https://de.cyverse.org](https://de.cyverse.org), and log in with your new account.

   <img width="881" alt="image" src="https://github.com/CU-ESIIL/hackathon2023_datacube/assets/3465768/41970a8d-c434-4075-9dd4-fbcd0f2ea07c">

   You should now see the Discovery Environment:

   <img width="881" alt="image" src="https://github.com/CU-ESIIL/hackathon2023_datacube/assets/3465768/0dcd0048-a4e3-469c-bd28-5a5574c5dec3">

4. We will give you permissions to access the Hackathon app. If you haven't already, let us know that you need access

## Open up an analysis with the hackathon environment (Jupyter Lab)

1. From the Cyverse Discovery Environment, click on `Apps` in the left menu
   ![apps](../assets/cyverse_basics/apps.png)

2. Select `JupyterLab ESIIL`
   ![use_this_app](../assets/cyverse_basics/use_this_app.png)

3. Configure and launch your analysis - when choosing the disk size, make sure to choose 64GB or greater. The rest of the settings you can change to suit your computing needs:
   ![app_launch](../assets/cyverse_basics/app_launch.png)

   ![app_settings](../assets/cyverse_basics/app_settings.png)

   ![launch](../assets/cyverse_basics/launch.png)

4. Click `Go to analysis`:
   ![go_to_analysis](../assets/cyverse_basics/go_to_analysis.png)

5. Now you should see Jupyter Lab!
   ![jupyterlab](../assets/cyverse_basics/jupyterlab.png)

## Set up your GitHub credentials

### If you would prefer to follow a video instead of a written outline, we have prepared a video here:
<a href="https://www.youtube.com/watch?v=nOwOzPJEQbU">
    <img src="https://img.youtube.com/vi/nOwOzPJEQbU/0.jpg" style="width: 100%;">
</a>

1. From Jupyter Lab, click on the Git Extension icon on the left menu:
   ![jupyterlab](../assets/cyverse_basics/jupyterlab.png)

2. Click `Clone a Repository` and Paste the link to the cyverse-utils [https://github.com/CU-ESIIL/cyverse-utils.git](https://github.com/CU-ESIIL/cyverse-utils.git) and click `Clone`:
   ![clone](../assets/cyverse_basics/clone.png)
   
3. You should now see the `cyverse-utils` folder in your directory tree (provided you haven't changed directories from the default `/home/jovyan/data-store`
   ![cyverse-utils](../assets/cyverse_basics/cyverse-utils.png)

4. Go into the `cyverse-utils` folder:
   ![click_cyverse_utils](../assets/cyverse_basics/click_cyverse_utils.png)

5. open up the `create_github_keypair.ipynb` notebook if you prefer Python or the 'create_github_keypair.R' script if you prefer R by double-clicking and then select the default 'macrosystems' kernel:
![open_cyverse_utils](../assets/cyverse_basics/open_cyverse_utils.png)

6. Now you should see the notebook open. Click the `play` button at the top. You will be prompted to enter your GitHub username and email:
   ![script_1](../assets/cyverse_basics/script_1.png)

   ![username](../assets/cyverse_basics/username.png)

   ![email](../assets/cyverse_basics/email.png)

7. You should now see your Public Key. Copy the WHOLE LINE including `ssh-ed25519` at the beginning and the `jovyan@...` at the end
![key](../assets/cyverse_basics/key.png)

8. Go to your GitHub settings page (you may need to log in to GitHub first):
   ![settings](../assets/cyverse_basics/settings.png)

9. Select `SSH and GPG keys`
   ![ssh](../assets/cyverse_basics/ssh.png)

10. Select `New SSH key`
   ![new_key](../assets/cyverse_basics/new_key.png)

11. Give your key a descriptive name, paste your ENTIRE public key in the `Key` input box, and click `Add SSH Key`. You may need to re-authenticate with your password or two-factor authentication.:
   ![paste_key](../assets/cyverse_basics/paste_key.png)

12. You should now see your new SSH key in your `Authentication Keys` list! Now you will be able to clone private repositories and push changes to GitHub from your Cyverse analysis!
   ![final](../assets/cyverse_basics/final.png)

> NOTE! Your GitHub authentication is ONLY for the analysis you're working with right now. You will be able to use it as long as you want there, but once you start a new analysis you will need to go through this process again. Feel free to delete keys from old analyses that have been shut down.
